from django.db import models

class Shop(models.Model):
    """Shops where players can buy and sell items"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏪')
    biome = models.CharField(max_length=50, blank=True, null=True, help_text="Shop appears only in this biome (empty = all biomes)")
    
    # Shop settings
    buy_price_multiplier = models.FloatField(default=1.0, help_text="Multiplier for buy prices")
    sell_price_multiplier = models.FloatField(default=0.5, help_text="Multiplier for sell prices (player sells to shop)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class ShopItem(models.Model):
    """Items available in a shop"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey('game.Material', on_delete=models.CASCADE)
    
    # Pricing
    base_buy_price = models.IntegerField(default=10, help_text="Base price for player to buy")
    base_sell_price = models.IntegerField(default=5, help_text="Base price for player to sell to shop")
    
    # Stock management
    stock = models.IntegerField(default=-1, help_text="-1 = unlimited stock")
    max_stock = models.IntegerField(default=-1, help_text="Maximum stock (-1 = no limit)")
    restock_rate = models.IntegerField(default=0, help_text="Items restocked per hour (0 = no restock)")
    last_restock = models.DateTimeField(auto_now_add=True)
    
    # Availability
    available = models.BooleanField(default=True)
    required_level = models.IntegerField(default=1, help_text="Player level required to purchase")
    
    class Meta:
        unique_together = ('shop', 'material')
        ordering = ['material__name']
    
    def __str__(self):
        return f"{self.shop.name} - {self.material.name}"
    
    @property
    def effective_buy_price(self):
        """Calculate effective buy price with shop multiplier"""
        return int(self.base_buy_price * self.shop.buy_price_multiplier)
    
    @property
    def effective_sell_price(self):
        """Calculate effective sell price with shop multiplier"""
        return int(self.base_sell_price * self.shop.sell_price_multiplier)


class Bank(models.Model):
    """Banks where players can deposit and withdraw money"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏦')

    # Bank location (appears on cells)
    cell = models.ForeignKey('game.MapCell', on_delete=models.CASCADE, related_name='banks', null=True, blank=True)

    # Bank fees
    deposit_fee_percent = models.FloatField(default=0.0, help_text="Fee percentage for deposits (0-100)")
    withdrawal_fee_percent = models.FloatField(default=0.0, help_text="Fee percentage for withdrawals (0-100)")

    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    """Record of all money transactions"""
    TRANSACTION_TYPES = [
        ('buy', 'Achat au magasin'),
        ('sell', 'Vente au magasin'),
        ('deposit', 'Dépôt à la banque'),
        ('withdrawal', 'Retrait à la banque'),
        ('reward', 'Récompense'),
        ('quest', 'Quête'),
        ('achievement', 'Succès'),
        ('admin', 'Administrateur'),
        ('other', 'Autre'),
    ]
    
    player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField(help_text="Positive = gain, negative = loss")
    balance_after = models.IntegerField(help_text="Player balance after transaction")
    description = models.TextField()
    
    # Optional references
    material = models.ForeignKey('game.Material', on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"{self.player.user.username}: {sign}{self.amount} coins ({self.transaction_type})"


class TradeOffer(models.Model):
    """Trade offers between players"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
        ('cancelled', 'Annulée'),
        ('completed', 'Complétée'),
        ('expired', 'Expirée'),
    ]

    # Players involved
    from_player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='trades_sent')
    to_player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='trades_received')

    # Offer details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Message optionnel")

    # What the initiator offers (JSON)
    offered_items = models.JSONField(default=list, help_text="[{'material_id': 1, 'quantity': 5}]")
    offered_money = models.IntegerField(default=0)

    # What the initiator wants
    requested_items = models.JSONField(default=list, help_text="[{'material_id': 2, 'quantity': 3}]")
    requested_money = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="Offre expire après ce temps")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Trade: {self.from_player.user.username} → {self.to_player.user.username} ({self.status})"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at and self.status == 'pending'

    def can_accept(self):
        """Check if trade can be accepted"""
        if self.status != 'pending':
            return False, "L'offre n'est plus en attente"
        if self.is_expired():
            return False, "L'offre a expiré"
        return True, None
