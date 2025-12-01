"""
Unit tests for trading service

Tests player-to-player trading, trade offers, and trade lifecycle.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from game.models import Player, Material, Inventory, TradeOffer
from game.services.trading_service import TradingService


class TradeCreationTests(TestCase):
    """Test trade offer creation"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='player1', password='pass')
        self.user2 = User.objects.create_user(username='player2', password='pass')
        self.player1 = Player.objects.create(user=self.user1, money=100)
        self.player2 = Player.objects.create(user=self.user2, money=100)

        self.wood = Material.objects.create(name='Wood', category='resource')
        self.stone = Material.objects.create(name='Stone', category='resource')

        # Player 1 has wood
        Inventory.objects.create(player=self.player1, material=self.wood, quantity=20)

    def test_create_simple_trade(self):
        """Test creating a simple trade offer"""
        offered_items = [{'material_id': self.wood.id, 'quantity': 5}]
        requested_items = []

        trade, error = TradingService.create_trade_offer(
            from_player=self.player1,
            to_player_id=self.player2.id,
            offered_items=offered_items,
            offered_money=0,
            requested_items=requested_items,
            requested_money=50
        )

        self.assertIsNotNone(trade)
        self.assertIsNone(error)
        self.assertEqual(trade.from_player, self.player1)
        self.assertEqual(trade.to_player, self.player2)
        self.assertEqual(trade.status, 'pending')

    def test_cannot_trade_with_self(self):
        """Test cannot create trade with yourself"""
        offered_items = [{'material_id': self.wood.id, 'quantity': 5}]

        trade, error = TradingService.create_trade_offer(
            from_player=self.player1,
            to_player_id=self.player1.id,
            offered_items=offered_items,
            offered_money=0,
            requested_items=[],
            requested_money=10
        )

        self.assertIsNone(trade)
        self.assertIn('vous-même', error)

    def test_cannot_offer_more_than_owned(self):
        """Test cannot offer more items than owned"""
        offered_items = [{'material_id': self.wood.id, 'quantity': 50}]

        trade, error = TradingService.create_trade_offer(
            from_player=self.player1,
            to_player_id=self.player2.id,
            offered_items=offered_items,
            offered_money=0,
            requested_items=[],
            requested_money=10
        )

        self.assertIsNone(trade)
        self.assertIn('insuffisante', error.lower())

    def test_cannot_offer_more_money_than_owned(self):
        """Test cannot offer more money than owned"""
        trade, error = TradingService.create_trade_offer(
            from_player=self.player1,
            to_player_id=self.player2.id,
            offered_items=[],
            offered_money=500,
            requested_items=[],
            requested_money=0
        )

        self.assertIsNone(trade)
        self.assertIn('insuffisant', error.lower())

    def test_trade_expires_after_duration(self):
        """Test trade offer has expiration time"""
        offered_items = [{'material_id': self.wood.id, 'quantity': 5}]

        trade, error = TradingService.create_trade_offer(
            from_player=self.player1,
            to_player_id=self.player2.id,
            offered_items=offered_items,
            offered_money=0,
            requested_items=[],
            requested_money=10,
            duration_hours=48
        )

        self.assertIsNotNone(trade)
        self.assertIsNotNone(trade.expires_at)
        # Should expire roughly 48 hours from now
        expected_expiry = timezone.now() + timedelta(hours=48)
        diff = abs((trade.expires_at - expected_expiry).total_seconds())
        self.assertLess(diff, 5)  # Within 5 seconds


class TradeAcceptanceTests(TestCase):
    """Test accepting trade offers"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='player1', password='pass')
        self.user2 = User.objects.create_user(username='player2', password='pass')
        self.player1 = Player.objects.create(user=self.user1, money=100)
        self.player2 = Player.objects.create(user=self.user2, money=100)

        self.wood = Material.objects.create(name='Wood', category='resource')
        self.stone = Material.objects.create(name='Stone', category='resource')

        # Player 1 has wood
        Inventory.objects.create(player=self.player1, material=self.wood, quantity=20)
        # Player 2 has stone
        Inventory.objects.create(player=self.player2, material=self.stone, quantity=15)

        # Create a trade offer: Player1 offers 5 wood for 10 stone
        self.trade = TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[{'material_id': self.wood.id, 'quantity': 5}],
            offered_money=0,
            requested_items=[{'material_id': self.stone.id, 'quantity': 10}],
            requested_money=0,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )

    def test_accept_trade_success(self):
        """Test successfully accepting a trade"""
        success, error = TradingService.accept_trade(self.trade.id, self.player2)

        self.assertTrue(success)
        self.assertIsNone(error)

        # Refresh players
        self.player1.refresh_from_db()
        self.player2.refresh_from_db()

        # Player1 should have stone now
        inv1_stone = Inventory.objects.get(player=self.player1, material=self.stone)
        self.assertEqual(inv1_stone.quantity, 10)

        # Player1 wood reduced
        inv1_wood = Inventory.objects.get(player=self.player1, material=self.wood)
        self.assertEqual(inv1_wood.quantity, 15)

        # Player2 should have wood now
        inv2_wood = Inventory.objects.get(player=self.player2, material=self.wood)
        self.assertEqual(inv2_wood.quantity, 5)

        # Player2 stone reduced
        inv2_stone = Inventory.objects.get(player=self.player2, material=self.stone)
        self.assertEqual(inv2_stone.quantity, 5)

        # Trade marked as completed
        self.trade.refresh_from_db()
        self.assertEqual(self.trade.status, 'completed')

    def test_accept_trade_with_money(self):
        """Test accepting trade with money exchange"""
        # Create trade with money: Player1 offers 20 coins for 5 stone
        trade = TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=20,
            requested_items=[{'material_id': self.stone.id, 'quantity': 5}],
            requested_money=0,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        success, error = TradingService.accept_trade(trade.id, self.player2)

        self.assertTrue(success)

        # Refresh players
        self.player1.refresh_from_db()
        self.player2.refresh_from_db()

        # Player1 money reduced, Player2 money increased
        self.assertEqual(self.player1.money, 80)
        self.assertEqual(self.player2.money, 120)

    def test_cannot_accept_without_requested_items(self):
        """Test cannot accept if don't have requested items"""
        # Player2 only has 15 stone, trade requests 10
        # Remove some stone
        inv = Inventory.objects.get(player=self.player2, material=self.stone)
        inv.quantity = 5
        inv.save()

        success, error = TradingService.accept_trade(self.trade.id, self.player2)

        self.assertFalse(success)
        self.assertIn('assez', error.lower())

    def test_cannot_accept_without_enough_money(self):
        """Test cannot accept if don't have enough money"""
        # Create trade requesting money
        trade = TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=0,
            requested_items=[],
            requested_money=200,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        success, error = TradingService.accept_trade(trade.id, self.player2)

        self.assertFalse(success)
        self.assertIn('insuffisant', error.lower())

    def test_cannot_accept_if_offerer_no_longer_has_items(self):
        """Test cannot accept if offerer sold items"""
        # Remove wood from player1
        inv = Inventory.objects.get(player=self.player1, material=self.wood)
        inv.quantity = 2
        inv.save()

        success, error = TradingService.accept_trade(self.trade.id, self.player2)

        self.assertFalse(success)
        self.assertIn('offrant', error.lower())


class TradeCancellationTests(TestCase):
    """Test canceling and rejecting trades"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='player1', password='pass')
        self.user2 = User.objects.create_user(username='player2', password='pass')
        self.player1 = Player.objects.create(user=self.user1, money=100)
        self.player2 = Player.objects.create(user=self.user2, money=100)

        self.wood = Material.objects.create(name='Wood', category='resource')
        Inventory.objects.create(player=self.player1, material=self.wood, quantity=20)

        self.trade = TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[{'material_id': self.wood.id, 'quantity': 5}],
            offered_money=0,
            requested_items=[],
            requested_money=50,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )

    def test_cancel_own_trade(self):
        """Test canceling your own trade offer"""
        success, error = TradingService.cancel_trade(self.trade.id, self.player1)

        self.assertTrue(success)
        self.assertIsNone(error)

        self.trade.refresh_from_db()
        self.assertEqual(self.trade.status, 'cancelled')

    def test_reject_received_trade(self):
        """Test rejecting a received trade"""
        success, error = TradingService.reject_trade(self.trade.id, self.player2)

        self.assertTrue(success)
        self.assertIsNone(error)

        self.trade.refresh_from_db()
        self.assertEqual(self.trade.status, 'rejected')

    def test_cannot_cancel_someone_elses_trade(self):
        """Test cannot cancel someone else's trade"""
        success, error = TradingService.cancel_trade(self.trade.id, self.player2)

        self.assertFalse(success)
        self.assertIsNotNone(error)

    def test_cannot_reject_own_trade(self):
        """Test cannot reject your own trade"""
        success, error = TradingService.reject_trade(self.trade.id, self.player1)

        self.assertFalse(success)
        self.assertIsNotNone(error)


class TradeListingTests(TestCase):
    """Test listing trades"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='player1', password='pass')
        self.user2 = User.objects.create_user(username='player2', password='pass')
        self.player1 = Player.objects.create(user=self.user1, money=100)
        self.player2 = Player.objects.create(user=self.user2, money=100)

        self.wood = Material.objects.create(name='Wood', category='resource')
        Inventory.objects.create(player=self.player1, material=self.wood, quantity=20)

    def test_get_received_trades(self):
        """Test getting trades received by player"""
        # Create 2 trades to player2
        TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=10,
            requested_items=[],
            requested_money=0,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=20,
            requested_items=[],
            requested_money=0,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        received = TradingService.get_received_trades(self.player2)

        self.assertEqual(received.count(), 2)

    def test_get_sent_trades(self):
        """Test getting trades sent by player"""
        TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=10,
            requested_items=[],
            requested_money=0,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        sent = TradingService.get_sent_trades(self.player1)

        self.assertEqual(sent.count(), 1)

    def test_completed_trades_not_in_pending(self):
        """Test completed trades don't appear in pending lists"""
        trade = TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=10,
            requested_items=[],
            requested_money=0,
            status='completed',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        received = TradingService.get_received_trades(self.player2)
        sent = TradingService.get_sent_trades(self.player1)

        self.assertEqual(received.count(), 0)
        self.assertEqual(sent.count(), 0)

    def test_get_trade_history(self):
        """Test getting trade history"""
        # Create completed trade
        TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=10,
            requested_items=[],
            requested_money=0,
            status='completed',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # Create rejected trade
        TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=20,
            requested_items=[],
            requested_money=0,
            status='rejected',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        history = TradingService.get_trade_history(self.player1)

        self.assertEqual(history.count(), 2)


class TradeExpirationTests(TestCase):
    """Test trade expiration"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='player1', password='pass')
        self.user2 = User.objects.create_user(username='player2', password='pass')
        self.player1 = Player.objects.create(user=self.user1, money=100)
        self.player2 = Player.objects.create(user=self.user2, money=100)

    def test_expire_old_trades(self):
        """Test expiring old pending trades"""
        # Create expired trade
        TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=10,
            requested_items=[],
            requested_money=0,
            status='pending',
            expires_at=timezone.now() - timedelta(hours=1)  # Already expired
        )

        # Create fresh trade
        TradeOffer.objects.create(
            from_player=self.player1,
            to_player=self.player2,
            offered_items=[],
            offered_money=20,
            requested_items=[],
            requested_money=0,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)  # Not expired
        )

        expired_count = TradingService.expire_old_trades()

        self.assertEqual(expired_count, 1)

        # Check status updated
        expired_trade = TradeOffer.objects.filter(
            expires_at__lt=timezone.now()
        ).first()
        self.assertEqual(expired_trade.status, 'expired')
