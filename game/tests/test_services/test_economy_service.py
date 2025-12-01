"""
Unit tests for economy service

Tests money management, transactions, and shop purchases.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player, Transaction, Shop, ShopItem, Material, Inventory
from game.services.economy_service import EconomyService


class MoneyManagementTests(TestCase):
    """Test money addition and removal"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, money=100)

    def test_add_money(self):
        """Test adding money to player"""
        initial_money = self.player.money

        trans = EconomyService.add_money(
            self.player,
            amount=50,
            transaction_type='reward',
            description='Quest reward'
        )

        self.player.refresh_from_db()
        self.assertEqual(self.player.money, initial_money + 50)
        self.assertIsNotNone(trans)
        self.assertEqual(trans.amount, 50)

    def test_add_money_creates_transaction(self):
        """Test adding money creates transaction record"""
        EconomyService.add_money(self.player, 25, 'sale', 'Sold item')

        trans = Transaction.objects.filter(player=self.player).first()
        self.assertIsNotNone(trans)
        self.assertEqual(trans.transaction_type, 'sale')
        self.assertEqual(trans.amount, 25)

    def test_add_money_negative_raises_error(self):
        """Test cannot add negative money"""
        with self.assertRaises(ValueError):
            EconomyService.add_money(self.player, -50)

    def test_remove_money(self):
        """Test removing money from player"""
        initial_money = self.player.money

        trans = EconomyService.remove_money(
            self.player,
            amount=30,
            transaction_type='purchase',
            description='Bought item'
        )

        self.player.refresh_from_db()
        self.assertEqual(self.player.money, initial_money - 30)
        self.assertEqual(trans.amount, -30)

    def test_remove_money_insufficient_funds(self):
        """Test cannot remove more money than available"""
        with self.assertRaises(ValueError) as context:
            EconomyService.remove_money(self.player, 500)

        self.assertIn('Insufficient funds', str(context.exception))

    def test_remove_money_negative_raises_error(self):
        """Test cannot remove negative money"""
        with self.assertRaises(ValueError):
            EconomyService.remove_money(self.player, -50)

    def test_transaction_records_balance(self):
        """Test transaction records balance after operation"""
        EconomyService.add_money(self.player, 50)

        trans = Transaction.objects.filter(player=self.player).first()
        self.assertEqual(trans.balance_after, 150)


class CanAffordTests(TestCase):
    """Test affordability checks"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, money=100)

    def test_can_afford_sufficient_funds(self):
        """Test can afford with sufficient funds"""
        can_afford = EconomyService.can_afford(self.player, 50)
        self.assertTrue(can_afford)

    def test_can_afford_exact_amount(self):
        """Test can afford exact amount"""
        can_afford = EconomyService.can_afford(self.player, 100)
        self.assertTrue(can_afford)

    def test_cannot_afford_insufficient_funds(self):
        """Test cannot afford with insufficient funds"""
        can_afford = EconomyService.can_afford(self.player, 150)
        self.assertFalse(can_afford)


class ShopPurchaseTests(TestCase):
    """Test shop item purchases"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, money=200)

        # Create shop
        self.shop = Shop.objects.create(
            name='General Store',
            description='A general store'
        )

        # Create material
        self.potion = Material.objects.create(
            name='Health Potion',
            category='consumable'
        )

        # Create shop item
        self.shop_item = ShopItem.objects.create(
            shop=self.shop,
            material=self.potion,
            base_buy_price=50,
            base_sell_price=25,
            stock=10
        )

    def test_buy_item_success(self):
        """Test successfully buying an item"""
        result = EconomyService.buy_item(
            self.player,
            self.shop_item,
            quantity=1
        )

        self.assertIsNotNone(result)
        self.player.refresh_from_db()

        # Money deducted
        self.assertEqual(self.player.money, 150)

        # Item added to inventory
        inventory = Inventory.objects.filter(
            player=self.player,
            material=self.potion
        ).first()
        self.assertIsNotNone(inventory)
        self.assertEqual(inventory.quantity, 1)

    def test_buy_multiple_items(self):
        """Test buying multiple quantities"""
        result = EconomyService.buy_item(
            self.player,
            self.shop_item,
            quantity=3
        )

        self.assertIsNotNone(result)
        self.player.refresh_from_db()

        # Money deducted (50 * 3 = 150)
        self.assertEqual(self.player.money, 50)

        # Items added
        inventory = Inventory.objects.get(
            player=self.player,
            material=self.potion
        )
        self.assertEqual(inventory.quantity, 3)

    def test_buy_item_insufficient_funds(self):
        """Test cannot buy with insufficient funds"""
        self.player.money = 30
        self.player.save()

        with self.assertRaises(ValueError) as context:
            EconomyService.buy_item(
                self.player,
                self.shop_item,
                quantity=1
            )

        self.assertIn('insuffisant', str(context.exception).lower())

    def test_buy_item_out_of_stock(self):
        """Test cannot buy when out of stock"""
        self.shop_item.stock = 2
        self.shop_item.save()

        with self.assertRaises(ValueError) as context:
            EconomyService.buy_item(
                self.player,
                self.shop_item,
                quantity=5
            )

        self.assertIn('stock', str(context.exception).lower())

    def test_buy_item_reduces_stock(self):
        """Test buying reduces shop stock"""
        initial_stock = self.shop_item.stock

        EconomyService.buy_item(self.player, self.shop_item, quantity=3)

        self.shop_item.refresh_from_db()
        self.assertEqual(self.shop_item.stock, initial_stock - 3)

    def test_buy_item_creates_transaction(self):
        """Test purchase creates transaction record"""
        EconomyService.buy_item(self.player, self.shop_item, quantity=1)

        trans = Transaction.objects.filter(
            player=self.player,
            transaction_type='buy'
        ).first()

        self.assertIsNotNone(trans)
        self.assertEqual(trans.amount, -50)


class SellItemTests(TestCase):
    """Test selling items"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, money=50)

        self.wood = Material.objects.create(
            name='Wood',
            category='resource'
        )

        # Add to inventory
        self.inventory = Inventory.objects.create(
            player=self.player,
            material=self.wood,
            quantity=20
        )

    def test_sell_item_success(self):
        """Test successfully selling an item"""
        # Create a shop that buys wood
        shop = Shop.objects.create(name='General Store', description='A general store')
        ShopItem.objects.create(
            shop=shop,
            material=self.wood,
            base_buy_price=10,
            base_sell_price=10,
            stock=0
        )

        result = EconomyService.sell_item(
            self.player,
            self.wood,
            quantity=5,
            shop=shop
        )

        self.assertIsNotNone(result)
        self.player.refresh_from_db()

        # Money added (5 * 5 = 25 with 0.5 sell multiplier, total 75)
        self.assertEqual(self.player.money, 75)

        # Inventory reduced
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 15)

    def test_sell_item_insufficient_quantity(self):
        """Test cannot sell more than owned"""
        shop = Shop.objects.create(name='General Store', description='A general store')
        ShopItem.objects.create(
            shop=shop,
            material=self.wood,
            base_buy_price=10,
            base_sell_price=10,
            stock=0
        )

        with self.assertRaises(ValueError) as context:
            EconomyService.sell_item(
                self.player,
                self.wood,
                quantity=30,
                shop=shop
            )

        self.assertIn('quantity', str(context.exception).lower())

    def test_sell_item_removes_from_inventory(self):
        """Test selling all removes from inventory"""
        shop = Shop.objects.create(name='General Store', description='A general store')
        ShopItem.objects.create(
            shop=shop,
            material=self.wood,
            base_buy_price=10,
            base_sell_price=10,
            stock=0
        )

        result = EconomyService.sell_item(
            self.player,
            self.wood,
            quantity=20,
            shop=shop
        )

        self.assertIsNotNone(result)

        # Inventory should be deleted
        exists = Inventory.objects.filter(
            player=self.player,
            material=self.wood
        ).exists()
        self.assertFalse(exists)

    def test_sell_item_creates_transaction(self):
        """Test selling creates transaction"""
        shop = Shop.objects.create(name='General Store', description='A general store')
        ShopItem.objects.create(
            shop=shop,
            material=self.wood,
            base_buy_price=10,
            base_sell_price=10,
            stock=0
        )

        EconomyService.sell_item(self.player, self.wood, quantity=5, shop=shop)

        trans = Transaction.objects.filter(
            player=self.player,
            transaction_type='sell'
        ).first()

        self.assertIsNotNone(trans)
        self.assertEqual(trans.amount, 25)  # 5 * 5 with 0.5 sell multiplier


class TransactionHistoryTests(TestCase):
    """Test transaction history"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, money=100)

    def test_get_transaction_history(self):
        """Test getting player transaction history"""
        # Create multiple transactions
        EconomyService.add_money(self.player, 50, 'reward')
        EconomyService.remove_money(self.player, 30, 'purchase')
        EconomyService.add_money(self.player, 20, 'sale')

        transactions = Transaction.objects.filter(player=self.player).order_by('-timestamp')

        self.assertEqual(transactions.count(), 3)

    def test_transaction_history_ordered(self):
        """Test transactions are ordered by date"""
        EconomyService.add_money(self.player, 10)
        EconomyService.add_money(self.player, 20)

        transactions = Transaction.objects.filter(player=self.player).order_by('-timestamp')

        # Should be most recent first
        self.assertGreaterEqual(
            transactions[0].timestamp,
            transactions[1].timestamp
        )

    def test_transaction_history_limit(self):
        """Test transaction history respects limit"""
        # Create 10 transactions
        for i in range(10):
            EconomyService.add_money(self.player, 10)

        transactions = Transaction.objects.filter(player=self.player).order_by('-timestamp')[:5]

        self.assertEqual(len(list(transactions)), 5)


class CreditCardTests(TestCase):
    """Test credit card payments"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            money=50,
            credit_card_balance=100
        )

        self.shop = Shop.objects.create(name='Store', description='A store')
        self.item_material = Material.objects.create(name='Item', category='tool')
        self.shop_item = ShopItem.objects.create(
            shop=self.shop,
            material=self.item_material,
            base_buy_price=80,
            base_sell_price=40,
            stock=10
        )

    def test_buy_with_credit_card(self):
        """Test buying with credit card when cash insufficient"""
        result = EconomyService.buy_item(
            self.player,
            self.shop_item,
            quantity=1,
            use_card=True
        )

        self.assertIsNotNone(result)
        self.player.refresh_from_db()

        # Money unchanged, card balance used
        self.assertEqual(self.player.money, 50)
        self.assertEqual(self.player.credit_card_balance, 20)

    def test_cannot_buy_insufficient_credit(self):
        """Test cannot buy if both cash and credit insufficient"""
        self.shop_item.base_buy_price = 200
        self.shop_item.save()

        with self.assertRaises(ValueError) as context:
            EconomyService.buy_item(
                self.player,
                self.shop_item,
                quantity=1,
                use_card=True
            )

        self.assertIn('solde', str(context.exception).lower())
