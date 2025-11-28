# Testing Guide

## Overview

This document provides comprehensive information about the testing infrastructure for the Crafting Game project.

## Test Structure

```
game/tests/
├── __init__.py
├── test_services/
│   ├── __init__.py
│   ├── test_skills_service.py      # 13 tests ✅
│   ├── test_equipment_service.py   # 10 tests ✅
│   └── (more to be added)
└── fixtures/
    └── (test data files)
```

## Running Tests

### All Tests
```bash
python manage.py test
```

### Specific Test Module
```bash
python manage.py test game.tests.test_services.test_equipment_service
```

### Specific Test Case
```bash
python manage.py test game.tests.test_services.test_equipment_service.EquipmentServiceTestCase
```

### Specific Test Method
```bash
python manage.py test game.tests.test_services.test_equipment_service.EquipmentServiceTestCase.test_equip_item_success
```

### With Options
```bash
# Keep test database (faster for repeated runs)
python manage.py test --keepdb

# Verbose output
python manage.py test -v 2

# Parallel execution
python manage.py test --parallel
```

## Test Coverage

### Skills Service (13 tests)
- ✅ Skill creation and retrieval
- ✅ XP awarding
- ✅ Level-up mechanics
- ✅ Talent unlocking
- ✅ Prerequisite checking
- ✅ Active effects

### Equipment Service (10 tests)
- ✅ Equipping items
- ✅ Unequipping items
- ✅ Slot management
- ✅ Inventory integration
- ✅ Error handling

## Writing New Tests

### Test Template

```python
from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player
from game.services.your_service import your_function


class YourServiceTestCase(TestCase):
    """Test suite for your service"""
    
    def setUp(self):
        """Create test data before each test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.player = Player.objects.create(user=self.user)
    
    def test_function_success(self):
        """Test successful execution"""
        result, status = your_function(self.player, valid_data)
        
        self.assertEqual(status, 200)
        self.assertIn('expected_key', result)
    
    def test_function_error_handling(self):
        """Test error cases"""
        result, status = your_function(self.player, invalid_data)
        
        self.assertEqual(status, 400)
        self.assertIn('error', result)
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** (`test_award_xp_levels_up_when_threshold_reached`)
3. **Test both success and failure cases**
4. **Use setUp for common test data**
5. **Clean, readable test code**

## Test Data

### Creating Test Players

```python
def setUp(self):
    self.user = User.objects.create_user(username='testuser')
    self.player = Player.objects.create(
        user=self.user,
        energy=100,
        health=100
    )
```

### Creating Test Materials

```python
self.material = Material.objects.create(
    name='Test Material',
    description='For testing',
    weight=1.0
)
```

### Creating Test Inventory

```python
self.inventory = Inventory.objects.create(
    player=self.player,
    material=self.material,
    quantity=10
)
```

## Continuous Integration

### Future Setup
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python manage.py test
```

## Test Coverage Reports

### Install Coverage
```bash
pip install coverage
```

### Run with Coverage
```bash
coverage run --source='game' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Next Steps

1. Add tests for remaining services:
   - gathering_service.py
   - movement_service.py
   - hunting_service.py
   - scavenging_service.py

2. Add integration tests for API endpoints

3. Add frontend component tests

4. Set up CI/CD pipeline

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
