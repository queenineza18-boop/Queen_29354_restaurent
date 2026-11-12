# Restaurant Order and Sales Tracking System (ROSTS)

Student Name: Queen Ineza  
Student ID: 29354  
Course: INSY 8311 – Database Development with PL/SQL  
Instructor:Eric Maniraguha  
Academic Year:2026–2027 (Semester I)  
Institution: Adventist University of Central Africa (AUCA)  

1. Problem Statement
Many growing restaurants and dining establishments in Kigali face operational bottlenecks caused by manual order-taking, fragmented paper receipts, and delayed sales reconciliation. Without an integrated database system, managers struggle to track daily revenue in real time, monitor raw ingredient depletion accurately, or prevent billing discrepancies. This manual workflow leads to revenue leakage, unexpected stockouts, and slower customer service.

 2. Objectives

 Main Objective
To design, implement, and automate a relational **Restaurant Order and Sales Tracking System (ROSTS)** using Oracle Database and PL/SQL that streamlines order management, enforces real-time inventory control, and provides actionable sales analytics.

 Objectives
1. Automate Order Processing:** Build PL/SQL stored procedures and functions to handle customer order entry, item pricing, and dynamic bill calculations accurately.
2. Enforce Real-Time Inventory Deduction:** Implement database triggers that automatically decrement raw ingredient stock levels upon order completion and block orders when stock is insufficient.
3. Ensure Security & Data Integrity:** Enforce business rules and maintain an automated audit log tracking sensitive data modifications and unauthorized access attempts.
4. Deliver Interactive Analytics:** Connect the Oracle database to an interactive Oracle APEX dashboard to visualize daily revenue KPIs, top-selling menu items, and low-stock alerts.

3. Data Source
* Dataset Name:** Restaurant Customer Orders, Menu Pricing, and Sales Transactions Dataset  
* Source Platform:** [Kaggle Datasets](https://www.kaggle.com/)  
* Dataset Size:** Over 10,000 anonymized transaction records covering menu categories, order timestamps, item quantities, and payment totals.  
* Licensing & Privacy:** Licensed for educational and non-commercial academic use; contains zero Personal Identifiable Information (PII).  

4. Innovation
* Selected Option: User Interface & Live Analytics Dashboard  
* Tool:Oracle APEX  
* Implementation Overview:A web-based operational interface connected directly to the Oracle Pluggable Database (PDB). Cashiers and waitstaff can record customer orders through simple forms that invoke underlying PL/SQL procedures, while restaurant managers monitor live daily revenue trends, popular menu items, and automated low-stock alerts.

5. Planned Tables & PL/SQL Features
Planned Relational Tables (3NF)
1. `BRANCHES`: Stores branch IDs, locations, contact information, and operational statuses.
2. `CATEGORIES`: Classifies menu items (e.g., Main Courses, Beverages, Desserts).
3. `MENU_ITEMS`: Stores item names, descriptions, unit prices, and category foreign keys.
4. `INGREDIENTS`: Tracks raw food ingredients, measurement units, and current stock quantities.
5. `RECIPE_ITEMS`: Maps menu items to required ingredient quantities for automated stock depletion.
6. `STAFF`: Maintains employee profiles, roles (Waiter, Chef, Cashier, Manager), and shift assignments.
7. `ORDERS`: Records order timestamps, table numbers, assigned staff IDs, and order statuses.
8. `ORDER_DETAILS`: Line items linking specific orders to menu items, quantities, and subtotals.
9. `PAYMENTS`: Tracks payment methods (Cash, Mobile Money, Card), timestamps, and final settled amounts.
10. `AUDIT_LOGS`: Captures database audit trails, user actions, and denied transaction attempts.

 PL/SQL Features
* Stored Procedures:`sp_process_new_order` to validate order inputs, insert order headers/details, and calculate subtotals.
* Functions:`fn_calculate_daily_revenue` to compute and return total daily sales revenue for a given branch and date.
* Cursors: Explicit cursors within reporting procedures to iterate through monthly sales figures and rank top-performing menu items.
* Triggers:
  * `trg_deduct_inventory`: A compound trigger that automatically updates ingredient stock levels when an order is finalized and raises an application error if stock is insufficient.
  * `trg_audit_orders`: A row-level audit trigger logging deletions or unauthorized price modifications into `AUDIT_LOGS`.
* Packages: `pkg_restaurant_ops` encapsulating all order management, inventory validation, and sales reporting procedures and functions.
