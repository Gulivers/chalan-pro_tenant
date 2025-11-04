-- Insert user manual for product creation
-- Using category ID 2 (User Manual)

INSERT INTO appcore_manualentry (
    title,
    slug,
    module,
    summary,
    content,
    is_active,
    created_at,
    updated_at,
    category_id
) VALUES (
    'User Manual: Creating Products with Prices',
    'user-manual-creating-products-prices',
    'Inventory',
    'Complete step-by-step guide for creating products, configuring prices, and performing transactions in the ChalanPro system. Includes practical examples, common problem solutions, and best practices.',
    '# 📦 User Manual: Creating Products with Prices

## 🎯 What You Will Learn in This Manual

This manual will teach you step-by-step how to create products in the ChalanPro system, configure their prices, and perform successful transactions. Upon completion, you will be able to:

- ✅ Create new products with complete information
- ✅ Configure prices for different customer types
- ✅ Handle different units of measure (pieces, rolls, gallons, etc.)
- ✅ Perform sales and purchases correctly
- ✅ Solve common problems

---

## 🚀 Step 1: Prepare Product Information

### Before creating a product, you need to have:

**📋 Basic Information:**
- **Product name**: Ex: "THHN Cable 12 AWG Black"
- **SKU code**: Ex: "THHN-12-BLK" (must be unique)
- **Category**: Ex: "Cables and Wires", "Electrical Equipment"
- **Brand**: Ex: "SIEMENS", "LEVITON" (optional)

**💰 Price Information:**
- **List price**: Base product price
- **Cost price**: What it costs you to buy it
- **Special prices**: For wholesalers, contractors, etc.

**📏 Measurement Information:**
- **Primary unit**: Is it sold by piece, by foot, by roll, by gallon?
- **Other units**: Can it also be sold in other presentations?

---

## 📝 Step 2: Create the Product

### 2.1 Access the Inventory Module

1. **Log in** to ChalanPro
2. **Navigate** to "Inventory" → "Products" menu
3. **Click** on "New Product"

### 2.2 Fill in Basic Information

**Required Fields:**
- **Name**: Descriptive product name
- **SKU**: Unique code (no spaces, use hyphens)
- **Category**: Select from dropdown list
- **Default Unit**: Primary sales unit

**Optional Fields:**
- **Brand**: If the product has a specific brand
- **Reorder Level**: Minimum quantity before restocking

### 2.3 Practical Example: THHN Cable

```
Name: THHN Cable 12 AWG Black
SKU: THHN-12-BLK
Category: Cables and Wires
Brand: SIEMENS
Default Unit: Foot (FT)
Reorder Level: 100
```

---

## 💰 Step 3: Configure Prices

### 3.1 Available Price Types

The system handles different price types:

| Type | Description | When to use |
|------|-------------|-------------|
| **LIST** | List price | Base reference price |
| **COST** | Cost price | To calculate profits |
| **SALE** | Sale price | Price for general public |
| **WHOLESALE** | Wholesale price | For large buyers |
| **CONTRACTOR** | Contractor price | For specialized contractors |

### 3.2 Configure Prices by Unit

**Example: THHN Cable with multiple presentations**

**Per Foot (primary unit):**
- LIST Price: $1.25 per foot
- COST Price: $0.81 per foot (65% of list price)
- WHOLESALE Price: $1.00 per foot (80% of list price)

**Per 250-foot Roll:**
- LIST Price: $275.00 per roll
- COST Price: $178.75 per roll

**Per 1000-foot Roll:**
- LIST Price: $1,050.00 per roll
- COST Price: $682.50 per roll

### 3.3 Configure Prices Step by Step

1. **In the "Prices" section** of the product form
2. **Click** on "Add Price"
3. **Select** the price type
4. **Select** the unit of measure
5. **Enter** the price
6. **Mark** if it''s the default price (only one per unit)
7. **Mark** if it''s used for sales and/or purchases
8. **Repeat** for each different price

---

## 🏪 Step 4: Configure Warehouse

### 4.1 Default Warehouse

The system needs to know which warehouse stores the product:

1. **Go** to "Inventory" → "Warehouses"
2. **Verify** that a warehouse marked as "Default" exists
3. **If it doesn''t exist**, create one and mark it as default

**Important**: There can only be one default warehouse in the entire system.

### 4.2 Configuration Example

```
Name: Main Warehouse
Location: Central Warehouse - Floor 1
Default: ✓ (marked)
Active: ✓ (marked)
```

---

## 🛒 Step 5: Perform Transactions

### 5.1 Create a Sale

1. **Go** to "Transactions" → "New Sale"
2. **Select** the customer
3. **Add products**:
   - Search for the product by name or SKU
   - The system automatically loads:
     - Default price
     - Default unit
     - Default warehouse
     - Product brand
4. **Adjust** if necessary:
   - Change quantity
   - Change unit (foot → roll)
   - Change price
   - Change warehouse
5. **Save** the transaction

### 5.2 Sale Line Example

```
Product: THHN Cable 12 AWG Black
Quantity: 50
Unit: Foot (FT)
Unit Price: $1.25
Discount: 0%
Subtotal: $62.50
Warehouse: Main Warehouse
Brand: SIEMENS
```

---

## 🔄 Step 6: Automatic Conversions

### 6.1 How It Works?

The system automatically converts between units:

**Examples:**
- You sell 1 roll of 250FT → System records 250 feet in inventory
- You sell 24 inches → System records 2 feet in inventory
- You buy 1 gallon → System records 1 gallon in inventory

### 6.2 Common Units

| Product | Purchase | Sale | Inventory |
|---------|----------|------|-----------|
| **Cables** | 250FT Rolls | By foot or roll | In total feet |
| **Pipes** | 10FT Sticks | By foot or stick | In total feet |
| **Switches** | Boxes of 25 | Individual | By piece |
| **Liquids** | Gallons | By gallon, quart or pint | In gallons |

---

## ⚠️ Common Problems and Solutions

### Problem 1: "No default price found"

**What does it mean?** The product doesn''t have a price marked as default.

**Solution:**
1. Go to the product
2. In the prices section
3. Mark one of the prices as "Default"
4. Save changes

### Problem 2: "No default warehouse"

**What does it mean?** The system doesn''t know where to store the product.

**Solution:**
1. Go to "Inventory" → "Warehouses"
2. Create a warehouse if it doesn''t exist
3. Mark it as "Default"
4. Make sure it''s active

### Problem 3: "SKU already exists"

**What does it mean?** There''s already another product with the same code.

**Solution:**
1. Change the SKU to a unique one
2. Use format: BRAND-TYPE-SIZE-COLOR
3. Example: "THHN-12-BLK" instead of "Black Cable"

### Problem 4: "Unit conversion fails"

**What does it mean?** The units are not configured correctly.

**Solution:**
1. Contact the system administrator
2. Verify that units of measure are configured
3. Make sure to use the correct units

---

## 📊 Tips to Improve Your Work

### ✅ Best Practices

**For Product Names:**
- Use descriptive and clear names
- Include important technical information
- Maintain consistency in format

**For SKUs:**
- Use short and easy-to-remember codes
- Include product information in the code
- Avoid spaces and special characters

**For Prices:**
- Always configure a default price
- Keep prices updated
- Use different types according to your business

**For Inventory:**
- Review reorder levels regularly
- Keep warehouses organized
- Update quantities after movements

### 🎯 Real Use Cases

**Case 1: Electrical Company**
- Products: Cables, switches, pipes
- Units: Feet, rolls, pieces
- Prices: LIST, COST, CONTRACTOR

**Case 2: Hardware Store**
- Products: Tools, materials
- Units: Pieces, boxes, gallons
- Prices: LIST, COST, WHOLESALE

**Case 3: Distributor**
- Products: Wide variety
- Units: Multiple per product
- Prices: All types available

---

## 🔍 Verify Everything Works

### Final Checklist

Before using the product in transactions, verify:

- [ ] **Product created** with unique name and SKU
- [ ] **Category assigned** correctly
- [ ] **Brand configured** if applicable
- [ ] **Default unit** selected
- [ ] **At least one price** configured
- [ ] **Default price** marked
- [ ] **Default warehouse** configured
- [ ] **Reorder level** established

### Quick Test

1. **Create a test sale** with the product
2. **Verify** that data loads automatically
3. **Change** unit and price if necessary
4. **Save** the transaction
5. **Check** that inventory updates correctly

---

## 📞 Need Help?

### Available Resources

**In the System:**
- **Contextual help**: Information icons in each field
- **Validations**: The system alerts you if something is missing
- **Error messages**: They tell you what to correct

**Contact:**
- **System administrator**: For technical problems
- **Supervisor**: For process questions
- **Technical manual**: For advanced information

### Updates

This manual is updated regularly. Always consult the latest version to get the most up-to-date information.

---

## ✨ Summary

Creating products in ChalanPro is a simple process when you follow these steps:

1. **Prepare** all necessary information
2. **Create** the product with basic data
3. **Configure** prices for different customer types
4. **Verify** that the default warehouse is configured
5. **Test** by creating a sample transaction

With this complete configuration, you will be able to perform sales and purchases efficiently and accurately.

**Your system is ready to handle products professionally!** 🎉',
    TRUE,
    NOW(),
    NOW(),
    2
);
