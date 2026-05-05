"""Thai baht amount to Thai words converter."""

_ONES = ['', 'หนึ่ง', 'สอง', 'สาม', 'สี่', 'ห้า', 'หก', 'เจ็ด', 'แปด', 'เก้า']
_TENS = ['', 'สิบ', 'ยี่สิบ', 'สามสิบ', 'สี่สิบ', 'ห้าสิบ', 'หกสิบ', 'เจ็ดสิบ', 'แปดสิบ', 'เก้าสิบ']

_PLACE = ['', 'สิบ', 'ร้อย', 'พัน', 'หมื่น', 'แสน', 'ล้าน']


def _three_digits_to_text(n: int) -> str:
    """Convert a number 1-999 to Thai words."""
    if n == 0:
        return ''
    hundreds = n // 100
    remainder = n % 100
    tens = remainder // 10
    ones = remainder % 10

    result = ''
    if hundreds:
        result += _ONES[hundreds] + 'ร้อย'

    if tens == 1:
        result += 'สิบ'
    elif tens:
        result += _TENS[tens]

    if ones == 1 and tens > 0:
        result += 'เอ็ด'
    elif ones:
        result += _ONES[ones]

    return result


def _integer_to_text(n: int) -> str:
    if n == 0:
        return 'ศูนย์'

    result = ''
    millions = n // 1_000_000
    remainder = n % 1_000_000

    if millions:
        result += _three_digits_to_text(millions) + 'ล้าน'
        # Handle millions > 999 (hundred millions, billions)
        # For cooperative loans, amounts stay under 10M so this is sufficient

    # remainder is 0-999999
    hundred_thousands = remainder // 100_000
    remainder %= 100_000
    ten_thousands = remainder // 10_000
    remainder %= 10_000
    thousands = remainder // 1_000
    remainder %= 1_000
    hundreds = remainder // 100
    remainder %= 100
    tens = remainder // 10
    ones = remainder % 10

    groups = [
        (hundred_thousands, 'แสน'),
        (ten_thousands, 'หมื่น'),
        (thousands, 'พัน'),
        (hundreds, 'ร้อย'),
    ]
    for digit, place in groups:
        if digit:
            result += _ONES[digit] + place

    if tens == 1:
        result += 'สิบ'
    elif tens:
        result += _TENS[tens]

    if ones == 1 and tens > 0:
        result += 'เอ็ด'
    elif ones == 1 and tens == 0 and (result or millions):
        result += 'เอ็ด'
    elif ones:
        result += _ONES[ones]

    return result


def baht_to_text(amount: float) -> str:
    """Convert a baht amount to Thai words.

    Example: 500000.0 → "ห้าแสนบาทถ้วน"
             500000.50 → "ห้าแสนบาทห้าสิบสตางค์"
    """
    if amount < 0:
        raise ValueError("amount must be non-negative")

    baht = int(amount)
    satang = round((amount - baht) * 100)

    baht_text = _integer_to_text(baht) + 'บาท'

    if satang == 0:
        return baht_text + 'ถ้วน'
    return baht_text + _integer_to_text(satang) + 'สตางค์'
