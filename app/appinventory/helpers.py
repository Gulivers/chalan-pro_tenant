from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

def convert_to_reference_unit(product, unit, quantity):
    # print("🧼 appinventory-helpers.py : This is convert_to_reference_unit")
    # print(f"🔍 Parámetros: product={product}, unit={unit}, quantity={quantity} (tipo: {type(quantity)})")
    
    """
    Convierte una cantidad a la unidad de referencia del producto.
    Si la conversión falla, devuelve la cantidad original o 0 como fallback.
    """
    if quantity is None:
        # print("❌ ERROR: convert_to_reference_unit recibió quantity=None")
        return Decimal('0.00')

    try:
        quantity = Decimal(quantity)
        # print(f"✅ Quantity convertido a Decimal: {quantity}")
    except (InvalidOperation, TypeError) as e:
        print(f"❌ ERROR al convertir quantity a Decimal: {e}")
        return Decimal('0.00')

    if not unit:
        # print("⚠️ Unit es None, devolviendo quantity sin conversión.")
        return quantity.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    if unit == product.unit_default:
        # print("✅ Unit es la unidad por defecto, devolviendo quantity sin conversión.")
        return quantity.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    factor = unit.conversion_factor
    sign = unit.conversion_sign
    # print(f"🔍 Factor: {factor}, Sign: {sign}")

    if not factor or factor <= 0:
        print("⚠️ Factor inválido, devolviendo quantity sin conversión.")
        return quantity.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    try:
        if sign == '*':
            result = quantity * factor
        elif sign == '/':
            result = quantity / factor
        else:
            result = quantity
        # print(f"✅ Resultado de conversión: {result}")
        return Decimal(result).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception as e:
        print(f"❌ Error en conversión matemática: {e}")
        return quantity.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
