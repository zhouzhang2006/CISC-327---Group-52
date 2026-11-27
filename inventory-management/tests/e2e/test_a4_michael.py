
from playwright.sync_api import Page, expect
from uuid import uuid4


BASE_URL = "http://127.0.0.1:5000"


def test_create_product_success(page: Page):
    page.goto(BASE_URL + "/ui/products")

    # Use a unique SKU so the test can run multiple times.
    sku = "TEST-" + uuid4().hex[:8]

    page.locator('input[name="name"]').fill("Test Keyboard")
    page.locator('input[name="sku"]').fill(sku)
    page.locator('input[name="unit_price"]').fill("25.99")
    page.locator('input[name="quantity_on_hand"]').fill("10")

    page.get_by_role("button", name="Add Product").click()
    print("Current URL:", page.url)
    print("Page content:", page.locator("body").inner_text())
    # Verify the product appears in the table.
    product_row = page.locator("tr").filter(has_text=sku)

    expect(product_row).to_have_count(1)
    expect(product_row).to_contain_text("Test Keyboard")
    expect(product_row).to_contain_text("25.99")
    expect(product_row).to_contain_text("10")


def test_create_product_missing_name(page: Page):
    page.goto(BASE_URL + "/ui/products")

    sku = "INVALID-" + uuid4().hex[:8]

    page.locator('input[name="name"]').fill("")
    page.locator('input[name="sku"]').fill(sku)
    page.locator('input[name="unit_price"]').fill("25.99")
    page.locator('input[name="quantity_on_hand"]').fill("10")

    page.get_by_role("button", name="Add Product").click()

    # The required Name field prevents submission.
    name_input = page.locator('input[name="name"]')

    assert name_input.evaluate(
        "(element) => element.validity.valueMissing"
    )

    # Verify the invalid product was not created.
    expect(page.locator("tr").filter(has_text=sku)).to_have_count(0)

