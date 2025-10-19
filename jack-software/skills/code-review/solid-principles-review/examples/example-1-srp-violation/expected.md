# Expected Behavior for Example 1

## Assertions

The skill MUST identify the following SRP violations:

### Primary Issue
- **Lines 6-50**: Order class has at least **5 distinct responsibilities**:
  1. Order calculation (calculate_total)
  2. Discount logic (apply_discount)
  3. Database persistence (save_to_database)
  4. Email notifications (send_confirmation_email)
  5. PDF generation (generate_invoice_pdf)

### Impact Statement
- Should mention: difficult to test in isolation
- Should mention: changes to one responsibility affect others
- Should mention: multiple reasons to change

### Suggested Refactoring
- Extract OrderCalculator for calculation logic
- Extract DiscountApplier or DiscountStrategy for discount logic
- Extract OrderRepository for persistence
- Extract OrderNotificationService for emails
- Extract InvoiceGenerator for PDF generation

## Success Criteria

✅ PASS if the skill:
- Identifies the Order class as having multiple responsibilities
- Lists at least 3-5 specific responsibilities
- Explains testability/maintainability impact
- Suggests extracting separate classes

❌ FAIL if the skill:
- Misses the SRP violation entirely
- Only identifies 1-2 responsibilities when there are 5
- Focuses on other issues (typing, performance, etc.) instead of SRP
