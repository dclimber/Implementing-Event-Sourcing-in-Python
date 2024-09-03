
Feature: Managing Orders with Event Sourcing

  Scenario: Creating an order
    Given a user with ID 1
    When the user creates an order
    Then the order should have the status "new"
    And the order should be saved with an event "OrderCreated"

  Scenario: Changing order status
    Given an existing order with status "new"
    When the order status is changed to "confirmed"
    Then the order status should be updated to "confirmed"
    And an event "StatusChanged" should be appended to the event stream
