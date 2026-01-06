from sec_company_facts import Company, get_cik_from_ticker
import pytest


def nonexistent_company_ticker():
    with pytest.raises(Exception):
        company = Company.from_ticker("NonexistentTicker")


def nonexistent_company_cid():
    with pytest.raises(Exception):
        _company = Company.from_ticker("9999999999")


def nonexistent_ticker():
    with pytest.raises(Exception):
        _cik = get_cik_from_ticker("9999999999")


def test_get_yearly_list():
    company = Company.from_ticker("MSFT")
    results = company.get_yearly(
        ["NonexistentTagHaha", "PaymentsOfDividendsCommonStock", "PaymentsOfDividends"]
    )
    assert len(results) > 5
    assert type(results[2019]) is int


def test_get_yearly_str():
    company = Company.from_ticker("MSFT")
    results = company.get_yearly("NetIncomeLoss")
    assert len(results) > 5
    assert type(results[2019]) is int


def test_get_yearly_empty():
    company = Company.from_ticker("MSFT")
    results = company.get_yearly("NonexistentTag")
    assert len(results) == 0


def test_get_yearly_empty_list():
    company = Company.from_ticker("MSFT")
    results = company.get_yearly(["NonexistentTag", "Also nonexistent"])
    assert len(results) == 0


def test_get_yearly_dataframe():
    company = Company.from_ticker("MSFT")
    df = company.get_yearly_dataframe(
        ["NetIncomeLoss", ["Booboo", "PaymentsForRepurchaseOfCommonStock"]]
    )
    assert "NetIncomeLoss" in df.columns
    assert "Booboo" in df.columns
    assert "PaymentsForRepurchaseOfCommonStock" not in df.columns
    assert len(df) > 5


def test_get_available_tags():
    company = Company.from_ticker("MSFT")
    tags = company.get_available_tags()
    assert type(tags) is list
    assert len(tags) > 5
    assert "NetIncomeLoss" in tags


def test_get_entity_name():
    company = Company.from_ticker("MSFT")
    name = company.get_entity_name()
    assert "microsoft" in name.lower()


def test_get_cik():
    company = Company.from_ticker("MSFT")
    cik = company.get_cik()
    assert int(cik) == int(get_cik_from_ticker("MSFT"))

    cid_company = Company.from_cik(cik)
    assert company.get_entity_name() == cid_company.get_entity_name()


def test_get_tag_label():
    company = Company.from_ticker("MSFT")
    label = company.get_tag_label("NetIncomeLoss")
    assert "income" in label.lower()


def test_get_tag_description():
    company = Company.from_ticker("MSFT")
    description = company.get_tag_description("NetIncomeLoss")
    assert "income" in description.lower()
