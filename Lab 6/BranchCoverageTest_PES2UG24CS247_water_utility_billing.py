import pytest

from water_utility_billing import (
    calculate_water_bill,
    check_meter_tampering
)


# 1. Input validation
def test_invalid_accounts_type():
    with pytest.raises(ValueError):
        calculate_water_bill("invalid", 10)


def test_negative_base_fee():
    with pytest.raises(ValueError):
        calculate_water_bill([], -10)


# 2. Account activation
def test_inactive_account():
    result = calculate_water_bill(
        [{"is_active": False, "usage_blocks": [50]}], 10
    )
    assert result["status"] == "NO_ACTIVITY"


def test_active_account():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [30]}], 10
    )
    assert result["status"] == "NORMAL"


# 3. Usage conditions
def test_zero_and_negative_usage():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [0, -5]}], 10
    )
    assert result["total_billed"] == 10


def test_usage_below_or_equal_50():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [30, 50]}], 10
    )
    assert result["total_billed"] == 130


def test_usage_between_51_and_100():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [60, 100]}], 10
    )
    assert result["total_billed"] == 410


# 4. Residential and commercial conditions
def test_residential_usage_above_100():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "is_commercial": False,
            "usage_blocks": [120, 30]
        }], 10
    )
    assert result["total_billed"] == 550


def test_commercial_usage_above_100():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "is_commercial": True,
            "usage_blocks": [120, 60]
        }], 10
    )
    assert result["total_billed"] == 580


# 5. Leak waiver conditions
def test_leak_waiver_above_200():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "has_leak_waiver": True,
            "usage_blocks": [120]
        }], 10
    )
    assert result["total_billed"] == 500


def test_leak_waiver_below_200():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "has_leak_waiver": True,
            "usage_blocks": [30]
        }], 10
    )
    assert result["total_billed"] == 55


def test_no_leak_waiver():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "has_leak_waiver": False,
            "usage_blocks": [120]
        }], 10
    )
    assert result["total_billed"] == 550


# 6. Flagged account conditions
def test_excessive_flags():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "usage_blocks": [0, -1, 0, -2, 0, -3]
        }], 10
    )
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_normal_flags():
    result = calculate_water_bill(
        [{
            "is_active": True,
            "usage_blocks": [0, -1]
        }], 10
    )
    assert result["status"] == "NORMAL"


# 7. No activity condition
def test_no_activity():
    result = calculate_water_bill([], 0)
    assert result["status"] == "NO_ACTIVITY"


def test_empty_usage_blocks():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": []}], 10
    )
    assert result["status"] == "NORMAL"


# 8. Meter tampering conditions
def test_no_meter_data():
    assert check_meter_tampering([]) == "NO_DATA"


def test_empty_meter_readings():
    assert check_meter_tampering([[]]) == "CLEAR"


def test_negative_reading():
    assert check_meter_tampering([[-5, 10]]) == "CLEAR"


def test_two_consecutive_negative_readings():
    assert check_meter_tampering([[-5, -10]]) == "TAMPER_SUSPECTED"


def test_negative_readings_reset():
    assert check_meter_tampering(
        [[-5, 10, -10, 20]]
    ) == "CLEAR"


def test_multiple_meters():
    assert check_meter_tampering(
        [[-5, 10], [-2, -3]]
    ) == "TAMPER_SUSPECTED"