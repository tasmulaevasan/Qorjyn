from config.ids import make_id


def test_make_id_survives_rapid_consecutive_calls():
    """Одной миллисекунды хватает на десятки вызовов.

    Голая метка времени давала одинаковые ключи двум записям одной
    операции — приём резерва пишет два события склада сразу.
    """
    ids = [make_id("evt") for _ in range(1000)]

    assert len(set(ids)) == 1000


def test_make_id_keeps_the_prefix_and_fits_the_column():
    generated = make_id("ord")

    assert generated.startswith("ord-")
    assert len(generated) <= 40
