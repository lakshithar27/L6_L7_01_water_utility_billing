import pytest

from water_utility_billing import (
    calculate_water_bill,
    check_meter_tampering
)


def test_invalid_accounts():
    with pytest.raises(ValueError):
        calculate_water_bill("invalid", 10)


def test_negative_base_fee():
    with pytest.raises(ValueError):
        calculate_water_bill([], -10)


def test_empty_accounts():
    result = calculate_water_bill([], 10)

    assert result["total_billed"] == 0
    assert result["status"] == "NO_ACTIVITY"


def test_inactive_account():
    accounts = [
        {
            "is_active": False,
            "usage_blocks": [50]
        }
    ]

    result = calculate_water_bill(accounts, 10)

    assert result["total_billed"] == 0
    assert result["status"] == "NO_ACTIVITY"


def test_residential_usage():
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "usage_blocks": [30, 60, 120, 40]
        }
    ]

    result = calculate_water_bill(accounts, 10)

    assert result["total_billed"] == 745
    assert result["status"] == "NORMAL"


def test_commercial_usage():
    accounts = [
        {
            "is_active": True,
            "is_commercial": True,
            "usage_blocks": [120, 60, 30, 0]
        }
    ]

    result = calculate_water_bill(accounts, 10)

    assert result["total_billed"] == 625
    assert result["status"] == "NORMAL"


def test_leak_waiver_applied():
    accounts = [
        {
            "is_active": True,
            "has_leak_waiver": True,
            "usage_blocks": []
        }
    ]

    result = calculate_water_bill(accounts, 250)

    assert result["total_billed"] == 200


def test_leak_waiver_not_applied():
    accounts = [
        {
            "is_active": True,
            "has_leak_waiver": True,
            "usage_blocks": []
        }
    ]

    result = calculate_water_bill(accounts, 150)

    assert result["total_billed"] == 150


def test_excessive_flags():
    accounts = [
        {
            "is_active": True,
            "usage_blocks": [0, -1, 0, -2, 0, -3]
        }
    ]

    result = calculate_water_bill(accounts, 10)

    assert result["status"] == "EXCESSIVE_FLAGS"


def test_no_meter_data():
    assert check_meter_tampering([]) == "NO_DATA"


def test_clear_meter_readings():
    readings = [
        [-1, 2, -1, 3],
        [4, 5, 6]
    ]

    assert check_meter_tampering(readings) == "CLEAR"


def test_meter_tampering():
    readings = [
        [-1, -2, 3]
    ]

    assert check_meter_tampering(readings) == "TAMPER_SUSPECTED"