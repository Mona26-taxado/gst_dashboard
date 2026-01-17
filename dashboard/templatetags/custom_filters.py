from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def number_to_words(value):
    """Convert number to words in Indian format"""
    try:
        num = int(float(value))
        if num == 0:
            return "Zero"
        
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        
        def convert_hundreds(n):
            result = ""
            if n >= 100:
                result += ones[n // 100] + " Hundred "
                n %= 100
            if n >= 20:
                result += tens[n // 10] + " "
                n %= 10
            elif n >= 10:
                result += teens[n - 10] + " "
                n = 0
            if n > 0:
                result += ones[n] + " "
            return result.strip()
        
        if num == 0:
            return "Zero"
        
        result = ""
        if num >= 10000000:  # Crores
            result += convert_hundreds(num // 10000000) + " Crore "
            num %= 10000000
        if num >= 100000:  # Lakhs
            result += convert_hundreds(num // 100000) + " Lakh "
            num %= 100000
        if num >= 1000:  # Thousands
            result += convert_hundreds(num // 1000) + " Thousand "
            num %= 1000
        if num > 0:
            result += convert_hundreds(num)
        
        return result.strip() + " Only"
    except (ValueError, TypeError):
        return "Zero Only"
 