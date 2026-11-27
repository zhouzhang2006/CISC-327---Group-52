from playwright.sync_api import Page, expect

SUPPLIERS_URL = "http://localhost:5000/ui/suppliers"


def test_add_supplier(page: Page):
	"""
	Goes to the supplier page and tests the add supplier form works. Ensuring the supplier is successfully added.
	"""
	page.goto(SUPPLIERS_URL)
	page.get_by_role("textbox", name="Name").fill("Test Supplier")
	page.get_by_role("textbox", name="Contact Email").fill("supplier@example.com")
	page.get_by_role("button", name="Add Supplier").click()

	supplier = page.get_by_role("row").last
	expect(supplier).to_contain_text("Test Supplier")
	expect(supplier).to_contain_text("supplier@example.com")


def test_blank_supplier(page: Page):
	"""Goes to supplier page and ensures the supplier form doesn't allow submitting a form with blank fields."""
	page.goto(SUPPLIERS_URL)
	submit = page.get_by_role("button", name="Add Supplier")
	table = page.get_by_role("row")
	existing_count = table.count()

	# Empty
	submit.click()
	expect(table).to_have_count(existing_count)  # header only

	# Missing contact email
	name = page.get_by_role("textbox", name="Name")
	name.fill("Test Supplier")
	submit.click()
	name.clear()
	expect(table).to_have_count(existing_count)  # header only

	# Missing name
	page.get_by_role("textbox", name="Contact Email").fill("supplier@example.com")
	submit.click()
	expect(table).to_have_count(existing_count)  # header only
