"""
Economy service for managing player money and transactions
"""
from django.db import transaction
from django.utils import timezone
from ..models import Player, Transaction, Shop, ShopItem, Inventory, Material
import logging

logger = logging.getLogger(__name__)


class EconomyService:
    """Service for managing player economy"""

    @staticmethod
    @transaction.atomic
    def add_money(player, amount, transaction_type='other', description='', material=None, shop=None):
        """
        Add money to player's account and record transaction
        
        Args:
            player: Player instance
            amount: Amount to add (positive integer)
            transaction_type: Type of transaction
            description: Description of the transaction
            material: Optional material reference
            shop: Optional shop reference
            
        Returns:
            Transaction instance
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        player.money += amount
        player.save()
        
        trans = Transaction.objects.create(
            player=player,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=player.money,
            description=description,
            material=material,
            shop=shop
        )
        
        logger.info(f"Added {amount} coins to {player.user.username}. New balance: {player.money}")
        return trans

    @staticmethod
    @transaction.atomic
    def remove_money(player, amount, transaction_type='other', description='', material=None, shop=None):
        """
        Remove money from player's account and record transaction
        
        Args:
            player: Player instance
            amount: Amount to remove (positive integer)
            transaction_type: Type of transaction
            description: Description of the transaction
            material: Optional material reference
            shop: Optional shop reference
            
        Returns:
            Transaction instance
            
        Raises:
            ValueError: If player doesn't have enough money
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if player.money < amount:
            raise ValueError(f"Insufficient funds. Has {player.money}, needs {amount}")
        
        player.money -= amount
        player.save()
        
        trans = Transaction.objects.create(
            player=player,
            transaction_type=transaction_type,
            amount=-amount,  # Negative for expense
            balance_after=player.money,
            description=description,
            material=material,
            shop=shop
        )
        
        logger.info(f"Removed {amount} coins from {player.user.username}. New balance: {player.money}")
        return trans

    @staticmethod
    def can_afford(player, amount):
        """Check if player can afford a purchase"""
        return player.money >= amount

    @staticmethod
    @transaction.atomic
    def buy_item(player, shop_item, quantity=1, use_card=False):
        """
        Player buys an item from a shop

        Args:
            player: Player instance
            shop_item: ShopItem instance
            quantity: Quantity to buy
            use_card: If True, pay with credit card; if False, pay with cash

        Returns:
            dict with transaction and inventory item

        Raises:
            ValueError: If purchase cannot be completed
        """
        # Validate
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if not shop_item.available:
            raise ValueError("Item is not available")

        if player.level < shop_item.required_level:
            raise ValueError(f"Requires level {shop_item.required_level}")

        # Check stock
        if shop_item.stock != -1:
            if shop_item.stock < quantity:
                raise ValueError(f"Insufficient stock. Available: {shop_item.stock}")

        # Calculate total cost
        total_cost = shop_item.effective_buy_price * quantity

        # Check if player can afford (with chosen payment method)
        if use_card:
            if player.credit_card_balance < total_cost:
                raise ValueError(f"Solde insuffisant sur la carte. Coût: {total_cost}₡, Solde: {player.credit_card_balance}₡")

            # Deduct from card
            player.credit_card_balance -= total_cost
            player.save()

            payment_method = "carte de crédit"
        else:
            if player.money < total_cost:
                raise ValueError(f"Argent liquide insuffisant. Coût: {total_cost}₡, Liquide: {player.money}₡")

            # Deduct from cash
            player.money -= total_cost
            player.save()

            payment_method = "argent liquide"

        # Create transaction record
        trans = Transaction.objects.create(
            player=player,
            transaction_type='buy',
            amount=-total_cost,
            balance_after=player.money,
            description=f"Acheté {quantity}x {shop_item.material.name} à {shop_item.shop.name} ({payment_method})",
            material=shop_item.material,
            shop=shop_item.shop
        )

        # Add to inventory
        inv_item, created = Inventory.objects.get_or_create(
            player=player,
            material=shop_item.material,
            defaults={'quantity': 0}
        )
        inv_item.quantity += quantity

        # Set durability for tools/equipment
        if shop_item.material.max_durability > 0 and inv_item.durability_max == 0:
            inv_item.durability_max = shop_item.material.max_durability
            inv_item.durability_current = shop_item.material.max_durability

        inv_item.save()

        # Update shop stock
        if shop_item.stock != -1:
            shop_item.stock -= quantity
            shop_item.save()

        logger.info(f"{player.user.username} bought {quantity}x {shop_item.material.name} for {total_cost} coins using {payment_method}")

        return {
            'transaction': trans,
            'inventory_item': inv_item,
            'total_cost': total_cost,
            'payment_method': payment_method
        }

    @staticmethod
    @transaction.atomic
    def sell_item(player, material, quantity, shop):
        """
        Player sells an item to a shop
        
        Args:
            player: Player instance
            material: Material instance
            quantity: Quantity to sell
            shop: Shop instance
            
        Returns:
            dict with transaction and earnings
            
        Raises:
            ValueError: If sale cannot be completed
        """
        # Validate
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check if player has the item
        try:
            inv_item = Inventory.objects.get(player=player, material=material)
        except Inventory.DoesNotExist:
            raise ValueError("You don't have this item")
        
        if inv_item.quantity < quantity:
            raise ValueError(f"Insufficient quantity. You have: {inv_item.quantity}")
        
        # Check if shop buys this item
        try:
            shop_item = ShopItem.objects.get(shop=shop, material=material)
        except ShopItem.DoesNotExist:
            raise ValueError("This shop doesn't buy this item")
        
        # Calculate earnings
        total_earnings = shop_item.effective_sell_price * quantity
        
        # Process sale
        trans = EconomyService.add_money(
            player,
            total_earnings,
            transaction_type='sell',
            description=f"Vendu {quantity}x {material.name} à {shop.name}",
            material=material,
            shop=shop
        )
        
        # Remove from inventory
        inv_item.quantity -= quantity
        if inv_item.quantity <= 0:
            inv_item.delete()
        else:
            inv_item.save()
        
        # Update shop stock
        if shop_item.max_stock != -1:
            shop_item.stock = min(shop_item.stock + quantity, shop_item.max_stock)
            shop_item.save()
        
        logger.info(f"{player.user.username} sold {quantity}x {material.name} for {total_earnings} coins")
        
        return {
            'transaction': trans,
            'total_earnings': total_earnings
        }
