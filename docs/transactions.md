# Transactions

From the user's point of view, there are 6 types of transactions in Kapytal. These are:

1. **Expense**
2. **Income**
3. **Buy**
4. **Sell**
5. **Transfer**
6. **Refund**

All of these transactions are sub-classes of the abstract base class (ABC) **Transaction**.

## Transaction attributes

The following attributes are shared by all **Transaction** implementations:

- User-input attributes
  - Date (datetime)
  - Description (string)
- Automatically generated attributes
  - Date created (datetime)
  - Date last edited (datetime)

## Cash transaction

The following extra attributes are added in the **CashTransaction** implementation (which implements both Income and Expense transactions):

- Account (CashAccount)
- Type (enum: Expense or Income)
- Payee (Attribute)
- Amount (Decimal)
- Currency (Currency)
- Category (Category or tuple of Categories)
- Tags (list of Attributes)
- Refund Transaction (RefundTransaction or None)

The Currency of the **CashTransaction** is the same as the Currency of the Account.

## Security transaction

The following extra attributes are added in the **SecurityTransaction** implementation (which implements both the Buy and Sell transactions):

- Security Account (SecurityAccount)
- Cash Account (CashAccount)
- Type (enum: Buy or Sell)
- Security (Security)
- Type of security (enum: ETF, Stock, Mutual Fund, bond etc.)
- Number of shares (int)
- Price per share (Decimal)
- Fees (Decimal)
- Total price (Decimal)
- Currency (Currency)

## Transfer transactions

There are two types of Transfer transactions - the **CashTransferTransaction** and the **SecurityTransferTransaction**

### **CashTransferTransaction** attributes

- From Account (CashAccount)
- To Account (CashAccount)
- From Amount (Decimal)
- To Amount (Decimal)
- From Currency (Currency)
- To Currency (Currency)
- Exchange Rate (Decimal)

### **SecurityTransferTransaction** attributes

- From Account (SecurityAccount)
- To Account (SecurityAccount)
- Security (Security)
- Number of shares (int)

## Refund transaction

The Refund transaction is a special transaction type. It esentially creates a new transaction that reverts a previously made **CashTransaction**. It has only the following attribute (on top of the default ones from **Transaction** class):

- Account (CashAccount)
- Amount (Decimal)
- Refunded Transaction (CashTransaction)

## Transaction class hierarchy

- Transaction (ABC)
  - CashTransaction
  - RefundTransaction
  - SecurityTransaction
  - TransferTransaction (ABC)
    - CashTransferTransaction
    - SecurityTransferTransaction
