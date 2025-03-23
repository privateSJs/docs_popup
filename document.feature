Feature: Dokumentacja parametrów systemu

  Scenario: Ustawienie różnych parametrów

    Given parametr 0x60C Status_of_stop ma wartość 122
    When parametr 0x60C Status_of_running zostaje zmieniony na 0
    Then powinienem zobaczyć status: error

  Scenario: Sprawdzenie parametru bez wartości

    When sprawdzam parametr 0x60A asdasda asda 2

  Scenario: Brak parametru

    When testuję nieistniejący parametr 0xFFF Unknown_param 1
