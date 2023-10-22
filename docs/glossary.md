# Glossary

This document contains succint descriptions of many terms one can encounter in Kapytal.

## Account

Accounts are "vessels", capable of containing items of monetary value.

There are two types of Accounts: [Cash Accounts](#cash-account-), which contain money denominated in a certain [Currency](#currency-), and [Security Accounts](#security-account-), which contain shares of [Securities](#security-).

In Kapytal, Accounts are disambiguated by their [path](#path). Account hierarchy can be created within [Account Tree](#account-tree-) using [Account Groups](#account-group-).

## Account Group ![Icon](../resources/icons/icons-16/folder.png)

Account Groups are folders containing [Accounts](#account) or other Account Groups. There is no limit to the depth of nesting within the [Account Tree](#account-tree-). Account Groups are disambiguated by their [path](#path).

## Account Item

Account Item is an umbrella term for [Accounts](#account) and [Account Groups](#account-group-).

## Account Tree ![Icon](../resources/icons/icons-16/folder-tree.png)

Account Tree is the second largest user interface feature of Kapytal, and it is the used to create, browse, edit, delete or otherwise manipulate [Accounts](#account) and [Account Groups](#account-group-). It is also the place where the balances of all Accounts and Account Groups are visible in both their [native](#native-currencyamount) and [base](#base-currency) [Currencies](#currency-).

Account Tree also offers an intuitive and easy to use interface shortcut to the Account [Transaction Filter](#transaction-filters-) via the check boxes in the rightmost Account Tree column. Only [Transactions](#transaction) related to the currently checked [Account Items](#account-item) are shown in the [Transaction Table](#transaction-table-).

Below the Account Tree there is a text label showing the total balance of currently selected Account Items in base Currency.

Account Tree can be hidden by toggling the ![Icon](../resources/icons/icons-16/folder-tree.png) "Show/Hide Account Tree" action in the toolbar. This is useful when more screen space for Transaction Table is required.

## Backups

Kapytal is creating backups of user JSON data file every time the file is opened or saved. Backups are created in all the directories listed within the Backups tab in [Settings Form](#settings-form-). Once the total size of all backups within a directory exceeds the size limit specified within the Settings Form Backups tab, Kapytal starts deleting old backups until the limit is satisfied again.

## Base Currency

In Kapytal, exactly one Currency at a time can be designated as base Currency. Base Currency is used in Base Balance column and Checked Account Balance widget in [Account Tree](#account-tree-), Base Amount column and Selected Transactions Total widget in [Transaction Table](#transaction-table-), and in [Reports](#reports).

The user can change the base Currency any time in [Currencies and Exchange Rates Form](#currencies-and-exchange-rates-form) in the Currencies section.

## Buy ![Icon](../resources/icons/icons-custom/certificate-plus.png)

Buy is a sub-type of [Security Transaction](#security-transaction) that represents the exchange of money from a [Cash Account](#cash-account-) for a gain of shares of a [Security](#security-) in a [Security Account](#security-account-).

## Cash

In Kapytal, Cash is synonym for money denominated in a certain [Currency](#currency-), regardless of whether it is physical (coins, bank notes) or digital (bank accounts, cryptocurrencies etc.). Kapytal is not capable of making a distinction between a physical or digital money.

Related terms are: [Cash Account](#cash-account-), [Cash Transaction](#cash-transaction) and [Cash Transfer](#cash-transfer-).

## Cash Account ![Icon](../resources/icons/icons-16/piggy-bank.png)

Cash Account is a type of [Account](#account) that can contain any amount of money denominated in a certain [Currency](#currency-). When creating a Cash Account, its native [Currency](#currency-) is defined by the user and can never be changed.

In practice, Cash Accounts can be used to represent physical money (in a wallet, at home etc.) or digital money (current bank accounts, savings bank accounts, credit card accounts, cryptocurrency wallets etc.).

Cash Accounts can contain positive, zero, or even negative amounts of money. Negative balance can be expected in a Cash Account representing a credit card. After paying off the debt, the balance of such Cash Account should return to zero.

Cash Accounts are used in all types of [Transactions](#transaction) except [Security Transfers](#security-transfer-).

Cash Accounts can have a non-zero initial balance. In Kapytal, initial balance is considered effective the day before the first Transaction of the given Cash Account.

## Cash Flow Reports ![Icon](../resources/icons/icons-16/chart.png)

Cash Flow Reports are [Reports](#reports) used for analyzing the flow of your money within a given period. Monthly, Annual and Total Cash Flow Reports are available. The data is shown in two tabs: Table and Chart.

In Table tab, double-clicking on any table cell (or selecting a table cell and selecting ![Icon](../resources/icons/icons-16/table.png) "Show Transactions" action) brings up a small version of a [Transaction Table](#transaction-table-) with all the [Transactions](#transaction) that were used for calculating the value of that table cell. The Transactions can be edited from this small Transaction Table.

Evaluated quantities are:

- Income
- Inward Transfers
  - [Cash Transfers](#cash-transfer-), [Security Transactions](#security-transaction) and [Security Transfers](#security-transfer-) transferring value from an unselected [Cash Account](#cash-account-) or [Security Account](#security-account-) to one of the selected [Account Items](#account-item)
- Refunds
- Initial Balances
  - see [Cash Account](#cash-account-) for more info
- Total Inflow
- Expenses
- Outward Transfers
  - same as Inward Transfers, but for value flowing out of the selected Account Items into the unselected Account Items
- Total Outflow
- Cash Flow
  - equal to Total Inflow - Total Outflow
  - Cash Flow is usually within one's control
- Securities Gain/Loss
- Currencies Gain/Loss
- Total Gain/Loss
- Net Growth
  - equal to Cash Flow + Total Gain/Loss
- [Savings Rate](#savings-rate)

## Cash Transaction

Cash Transactions are [Transactions](#transaction) that represent the transfer of money between a [Cash Account](#cash-account-) and a [Payee](#payee-). There are two types of Cash Transactions: [Income](#income-) and [Expense](#expense-).

Cash Transactions can contain multiple Categories (so-called "split Categories").

Cash Transaction specific attributes are: [Cash Account](#cash-account-), [Payee](#payee-), Amount and [Categories](#category-).

## Cash Transfer ![Icon](../resources/icons/icons-custom/coins-arrow.png)

Cash Transfers are [Transactions](#transaction) that can transfer money from one [Cash Account](#cash-account-) to another. The [Currencies](#currency-) of the Cash Accounts do not have to match, and Cash Transfers can therefore represent Currency exchange operations.

Cash Transfer specific attributes are: Sender Cash Account, Recipient Cash Account, amount sent, amount received.

## Category ![Icon](../resources/icons/icons-custom/category.png)

Categories are attributes that can be used in [Cash Transactions](#cash-transaction) and [Refunds](#refund-). The user can create any amount of Categories, and Categories can form a tree-like hierarchy. The user can use Categories to filter [Transactions](#transaction) or create specific Category [Reports](#reports).

Each Category is defined by its [path](#path) and type (Income, Expense, Income and Expense). Income Categories can only be used in [Income](#income-) Cash Transactions, Expense Categories can only be used in [Expense](#expense-) Cash Transactions and Income and Expense Categories can be used in any Cash Transactions.

Categories are meant to be rather generic and "reused" often. [Tags](#tag-) are better suited as an "one-off" attribute.

- Example Income Categories: "Employment/Salary", "Employment/Benefits", "Employment/Bonus", "Tax Refund".
- Example Expense Categories: "Food and Drink/Eating out", "Food and Drink/Groceries", "Bills/Heating", "Health/Medicine", "Housing/Rent", "Housing/Equipment/Kitchen", "Transport/Airplane", "Car/Fuel", "Car/Repairs", "Clothes/Accessories", "Sports/Equipment", "Leisure/Culture/Theatre".
- Example Income and Expense Categories: "Interest", "Gift".

Contrary to many similar software, in Kapytal, the user can assign Categories to Cash Transactions regardless of how many children the Categories have. For example, the user can use Category "Food and Drink" as well as "Food and Drink/Eating out", and both could be even assigned to the same Cash Transactions at the same time.

## Currencies and Exchange Rates Form

Currencies and Exchange Rates Form is the [Form](#form) for creating, editing, deleting, manipulating and updating [Currencies](#currency-), [Exchange Rates](#exchange-rate-) and Exchange Rate quotes.

## Currency ![Icon](../resources/icons/icons-custom/currency.png)

In Kapytal, Currencies are units of money. The user can create Currencies in [Currencies and Exchange Rates Form](#currencies-and-exchange-rates-form). Currencies have two attributes: code and number of decimals. These two attributes are specified upon Currency creation and can never be changed.

Code is a 3-letter string, as the intended contents are the [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) standard codes (such as "USD", "EUR" etc.). However, in practice, the user can enter any three letter string. Kapytal Currencies can therefore be used to represent non-ISO4217 currencies such as cryptocurrencies ("BTC", "ETH") or any other unit of monetary value.

Number of decimals represents the number of digits after the decimal separator for the given Currency. Most currencies have 2 decimals (see column "D" [here](https://en.wikipedia.org/wiki/ISO_4217#List_of_ISO_4217_currency_codes)). Cryptocurrencies such as Ethereum can however have up to 18 decimals. Kapytal therefore supports up to 18 decimal places. In general, Kapytal does not allow the user to specify amounts with more decimals than the specified Currency number of decimals, with the exception of [Security](#security-) price. When specifying Security price per share in [Security Form](#securities-form) or [Security Transactions](#security-transaction), Kapytal allows the user to enter the price with greater precision than the number of digits of the given Currency.

In Kapytal, exactly one Currency at a time can be designated as [base Currency](#base-currency).

To represent Currency exchange, use [Cash Transfers](#cash-transfer-), as sending and receiving Cash Accounts do not have to have the same Currency.

## Date

All [Transactions](#transaction) contain date attribute, as well as [Security](#security-) price and [Exchange Rate](#exchange-rate-) quotes.

The user can set the format of date attributes in [Settings Form](#settings-form-), separately for Transactions and for other purposes. This is because under the hood, Transaction dates also contain hours, minutes and seconds, which are hidden by default. Setting a date format which contains hours, minutes or seconds can show them within the Transaction Table. This can be useful when reordering Transactions using the hours and minutes, as Transaction creation/edit dialogs date widgets contain hours and minutes. Seconds are not editable, as they are reserved for Kapytal's internal purposes.

## Demo File

Demo file is a JSON file distributed within Kapytal installation and can be found at `<installation_directory>/Kapytal/_internal/saved_data/demo.json`. It contains fictitous data and showcases the typical usage of Kapytal features.

## Description

Descriptions are optional strings describing [Transactions](#transaction). They can be multi-line and up to 256 characters long.

## Dialog

In Kapytal, Dialogs are "disposable" user interface elements/windows used for simple data entry tasks (note this is not a clear cut definition). Dialogs usually disappear after accepting them.

## Exchange Rate ![Icon](../resources/icons/icons-custom/currency-arrow.png)

Exchange Rates relate two [Currencies](#currency-) together through a numerical conversion factor. Exchange Rates can be created within [Currencies and Exchange Rates Form](#currencies-and-exchange-rates-form).

Both current or past values of Exchange Rates can be set manually within [Currencies and Exchange Rates Form](#currencies-and-exchange-rates-form). Current rates can also be downloaded automatically via [Update Quotes Form](#update-quotes-form-).

## Expense ![Icon](../resources/icons/icons-custom/coins-minus.png)

Expense is a sub-type of [Cash Transaction](#cash-transaction), which represents the transfer of money from a [Cash Account](#cash-account-) to a [Payee](#payee-). Unlike [Income](#income-), Expense can be refunded by a [Refund](#refund-). Once an Expense is refunded, it cannot be edited anymore.

## Form

In Kapytal, Forms are user interface elements/windows used for more complex settings and operations (note this is not a clear cut definition). Operations within Forms usually create [Dialogs](#dialog).

These are some of the Forms in Kapytal:

- [Category](#category-) Form
- [Currencies and Exchange Rates Form](#currencies-and-exchange-rates-form)
- [Payee](#payee-) Form
- [Update Quotes Form](#update-quotes-form-)
- [Securities Form](#securities-form)
- [Settings Form](#settings-form-)
- [Tags](#tag-) Form
- [Transaction Filter](#transaction-filters-) Form

## Income ![Icon](../resources/icons/icons-custom/coins-plus.png)

Income is a sub-type of [Cash Transaction](#cash-transaction), which represents the transfer of money from a [Payee](#payee-) to a [Cash Account](#cash-account-). Unlike [Expense](#expense-), Income cannot be [refunded](#refund-).

## Logging

Most operations the user makes within Kapytal are logged in a log file. These files are used for debugging purposes and can be found within `<installation_directory>/Kapytal/_internal/logs/`.

The user can set the maximum logs directory size in [Settings Form](#settings-form-). Once exceeded, Kapytal will start deleting logs upon startup, starting from the oldest logs, until the limit is satisfied.

## Native Currency/Amount

The [Currency](#currency-) of a [Cash Account](#cash-account-) is considered to be its native Currency.

In the [Account Tree](#account-tree-), the balance of all Cash Accounts is shown in both native and [base](#base-currency) Currency, unless the native Currency of the particular Cash Account matches the base Currency. In that case, native balance is empty (as it would be identical to base amount anyway).

In the [Transaction Table](#transaction-table-), Native amount and Base amount are two separate columns. Native amount displays the amount of all [Transactions](#transaction) except the [Cash Transfer](#cash-transfer-) and [Security Transfer](#security-transfer-) Transactions, which are denominated in a Currency different from the base Currency.

## Net Worth Reports ![Icon](../resources/icons/icons-16/chart-pie.png)

Net Worth Reports are [Reports](#reports) used for high level overview of total financial assets.

Net Worth Reports only take [Account Items](#account-item) passing through the Account Filter into account.

There are three Net Worth Reports:

- Accounts
  - used for visualizing how much each Account Item from [Account Tree](#account-tree-) is worth
- Asset Type
  - used for calculating and visualizing how much net worth within selected Account Items consists of money denominated in specific [Currencies](#currency-) or money tied up in specific [Securities](#security-)
- Time
  - used for visualizing the time evolution of selected Account Items

## Path

In Kapytal, items in tree-like hierarchies ([Account Items](#account-item) or [Categories](#category-)) are identified by their path. The path string consists of item names separated by slashes, starting from root item: `Grandparent Name/Parent Name/Item Name`.

## Payee ![Icon](../resources/icons/icons-16/user-business.png)

Payee is an attribute appearing in [Cash Transactions](#cash-transaction) and represents the other party of the Cash Transactions. Payees are identified only by their name, which can contain any symbols excluding colons (":").

In case of [Income](#income-), the Payee could be an employer, customer, the bank paying the user savings account interest, the government sending them the tax refund etc. In case of [Expense](#expense-), the Payee could be a landlord, telephone company, local grocery shop, gym etc.

Payees can be used to filter Cash Transactions or create specific Payee [Reports](#reports).

## Refund ![Icon](../resources/icons/icons-custom/coins-arrow-back.png)

Refund is a special type of [Transaction](#transaction) that "reverts" the effects of an [Expense](#expense-). The user can create a Refund by right-clicking an Expense in [Transaction Table](#transaction-table-) and selecting "Add Refund".

Refunds can refund the Expense fully or partially. Each Refund can relate to only one Expense, while each Expense can be refunded by multiple Refunds. However, the total sum of refunded money cannot exceed the total amount defined by the Expense.

Refunds can refund money to a different [Cash Account](#cash-account-) than the Cash Account defined in the refunded Expense. The date & time of a Refund cannot be earlier than the date & time of the refunded Expense.

To find Refund's refunded Expense, or to find refunded Expense's Refunds, right-click the chosen Transaction and select "Find related".

For the purposes of most [Reports](#reports), Refunds are either treated separately, or as "inverted" Expense. Refunds are never considered as [Income](#income-).

## Reports

Reports are used to analyse and visualize your data using charts and tables. Reports can be accessed via the "Reports" menu item.

Note reports always analyse only the [Transactions](#transaction) or [Account Items](#account-item) that are passing through [Transaction Filters](#transaction-filters-). The user can use this to their advantage, for example to remove some Transactions from the analysed data set etc.

There are several types of Reports:

- [Net Worth Reports](#net-worth-reports-)
- [Cash Flow Reports](#cash-flow-reports-)
- Category Reports
- Tags Reports
- Payee Reports

## Savings Rate

Savings Rate is a quantity evaluated in [Cash Flow Reports](#cash-flow-reports-).

Savings Rate quantifies saved money relative to the sum of all saveable money for a given period. [Refunds](#refund-) contribute towards the saved amount, but not towards the saveable amount, therefore Savings Rate of more than 100% is theoretically possible.

The formula is: Savings Rate = Cash Flow / (Income + Inward Transfers) = (Inflows - Outflows) / (Inflows - Refunds)

## Securities Form

Securities Form is the [Form](#form) for creating, editing, deleting, manipulating and updating [Securities](#securities-form) and their price quotes. In the Overview tab, an overview of Securities and all Security Accounts which contain their shares is available.

## Security ![Icon](../resources/icons/icons-16/certificate.png)

Securities are used to represent asserts of monetary value which fluctuates over time, such as stocks, bonds, ETFs, pension funds and other financial instruments, as well as real estate, [mortgages](./faq.md#how-to-handle-a-mortgage-in-kapytal), cars, art etc.

In Kapytal, shares of Securities can be owned within [Security Accounts](#security-account-), can be acquired or sold via [Security Transactions](#security-transaction), and can be transfered to other Security Accounts via [Security Transfers](#security-transfer-).

Price history of Securities can be tracked by Kapytal. Prices for a specific calendar day can be entered manually or loaded from a CSV file in [Securities Form](#securities-form), or updated automatically in [Update Quotes Form](#update-quotes-form-).

When creating a Security in Securities Form, following attributes are requested:

- Name
- Symbol
  - optional, but required for automatic price updates via [Update Quotes Form](#update-quotes-form-)
- Type
  - custom string of your own choosing (for example "ETF", "Real Estate", "Pension Fund" etc.)
- Unit
  - smallest unit of Security (typical value is 1, but some Securities can be owned in fractions like 0.001 etc.)
- [Currency](#currency-)

## Security Account ![Icon](../resources/icons/icons-16/bank.png)

Security Account is a type of [Account](#account) that can contain shares of [Securities](#security-). Unlike [Cash Accounts](#cash-account-), which can contain only money of single [Currency](#currency-), Security Accounts can contain shares of any number of various Securities, and the Securities do not even have to be denominated in the same Currency.

There is no Currency associated with Security Accounts. In [Account Tree](#account-tree-), their balance is shown only in terms of the [base Currency](#base-currency).

In practice, Security Accounts can be used to represent investment or trading accounts or pension scheme accounts, but also real estate portfolio, cars, art collection or any group of assets whose fluctuating value the user wants to track in Kapytal.

Security Accounts can contain positive, zero, or even negative amounts of shares of any Security. Negative amounts of shares are usually an indicator of user error.

To see the Security contained within a Security Account, right-click the Security Account in the Accoutn Tree and select "Show Securities" option from the context menu. The contents of a Security Account can also be seen from a different point of view by navigating to Edit/Securities form and switching to the "Overview" tab.

Security Accounts are used in [Security Transactions](#security-transaction) and [Security Transfers](#security-transfer-).

## Security Transaction

Security Transactions are [Transactions](#transaction) that represent buying or selling shares of a [Security](#security-) in exchange for monetary value. There are two sub-types of Security Transactions: [Buy](#buy-) and [Sell](#sell-).

Security Transaction specific attributes are: [Cash Account](#cash-account-), [Security Account](#security-account-), Security, shares, price per share.

## Security Transfer ![Icon](../resources/icons/icons-custom/certificate-arrow.png)

Security Transfers are [Transaction](#transaction) that can transfer shares of a [Security](#security-) from one [Security Account](#security-account-) to another.

Security Transfer specific attributes are: Sender Security Account, Recipient Security Account, Security, shares.

## Sell ![Icon](../resources/icons/icons-custom/certificate-minus.png)

Sell is a sub-type of [Security Transaction](#security-transaction) that represents the exchange of shares of a [Security](#security-) from a [Security Account](#security-account-) for a gain of money in a [Cash Account](#cash-account-).

Note Kapytal allows negative shares of a Security within Security Account, i.e. it is possible to use Sell to sell shares of Security from a Security Account that does not contain any shares of that Security at all. This can be leveraged for [modelling mortgages](./faq.md#how-to-handle-a-mortgage-in-kapytal).

## Settings Form ![Icon](../resources/icons/icons-16/gear.png)

Settings Form is used to change internal Kapytal settings, such as the date formats, backup file sizes and paths, and log sizes.

## Tag ![Icon](../resources/icons/icons-16/tag.png)

Tags are attributes that can be used in any [Transaction](#transaction). The user can create any amount of Tags. Tags are identified only by their name, which can contain any symbols excluding colons (":"). The user can use Tags to filter Transactions or create specific Tag [Reports](#reports).

Tags can be used to distinguish Transactions related to certain events ("vacation Greece 06/2023", "Christmas 2019", "my wedding", "dates with Eve", "house renovation 2017"), people ("baby", "friends", "together"), places ("7 Sunny Street" - for example when the user wants to distinguish all Transactions related to their house), Transactions the user wants someone to repay them for ("Adam owes me") etc.

Tags are not meant for describing the object of the Transactions (i.e. "Groceries", "Electronics", "Rent" etc.) as that is the purpose of [Categories](#category-).

## Transaction

Transactions are used to represent all real-world Transactions the user has made.

There are several types of Transactions: [Cash Transactions](#cash-transaction), [Cash Transfers](#cash-transfer-), [Refunds](#refund-), [Security Transactions](#security-transaction) and [Security Transfers](#security-transfer-).

All Transaction types contain the following attributes: [Date](#date), Description and [Tags](#tag-).

## Transaction Filters ![Icon](../resources/icons/icons-16/funnel.png)

Transaction Filters are used to filter [Transactions](#transaction) based on specific criteria. Transaction Filter Form can be accessed by clicking on the funnel icon next to the [Transaction Table](#transaction-table-) search bar.

There are many Transaction Filters:

- Type Filter
- Date Filter
- Description Filter
- Account Filter
  - mostly accessed directly from the [Account Tree](#account-tree-) check boxes
  - it filters Transactions based on the [Account Items](#account-item) they relate to, but also the Account Items themselves (mainly for [Net Worth Report](#net-worth-reports-) purposes)
- Tag Filters
  - Tag-less Transaction Filter
  - Specific Tag Filter
  - Split Tags Transaction Filter
- Category Filters
  - Specific Category Filter
  - Split Category Filter
- Payee Filter
- Currency Filter
- Cash Amount Filter
- Security Filter
- [UUID](#uuid) Filter

Transaction Filters are chained one after another, and only Transactions passing through all active filters are shown in the Transaction Table.

Many Transaction Filters have three "modes": off, keep and discard. Filters which are off do not discard any Transactions. Filters which are set to "keep" mode keep the Transactions which satisfy their criteria, while filters set to "discard" mode do the opposite of "keep" mode filters and discard the Transactions which satisfy their criteria instead.

## Transaction Table ![Icon](../resources/icons/icons-16/table.png)

Transaction Table is the dominant user interface feature of Kapytal, and it is the interface used to create, browse, edit, delete or otherwise manipulate [Transactions](#transaction).

Transaction Table contains many columns, some of which are not shown by default. The columns can be manipulated via the context menu shown by right-clicking on the Transaction Table column headers.

Below the Transaction Table, there are two text labels. First label shows the amount of currently shown Transactions out of the total amount of Transactions. Transactions can be hidden from Transaction Table via [Transaction Filters](#transaction-filters-). Second label shows the sum of the amounts of currently selected Transactions. Please note only [Income](#income-), [Expense](#expense-) and [Refund](#refund-) amounts are summed.

Transaction Table can be hidden by toggling the ![Icon](../resources/icons/icons-16/table.png) "Show/Hide Transaction Table" action in the toolbar.

## UUID

Universally Unique IDentifier is a string of characters which unambiguously identifies an object. In Kapytal, all [Transactions](#transaction) have an UUIDv4, which can be shown in the [Transaction Table](#transaction-table-) by right-clicking the Transaction Table header and enabling the UUID column in the context menu. Transaction UUIDs can also be copied to clipboard by right-clicking selected Transactions in the Transaction Table and selecting the Copy UUIDs action in the context menu. The user can paste the clipboard contents into the UUID [Transaction Filter](#transaction-filters-) directly.

Under the hood, all [Account Items](#account-item), [Securities](#security-) and [Categories](#category-) are also assigned an UUID. Account Item and Security UUIDs can be found in the JSON file, while Category UUIDs are assigned randomly during program runtime.

## Update Quotes Form ![Icon](../resources/icons/icons-16/arrow-circle-double.png)

Update Quotes Form is a [Form](#form) used to fetch latest [Security](#security-) price and [Exchange Rate](#exchange-rate-) data from Yahoo Finance. Only Securities with non-empty symbol strings are eligible for price update.