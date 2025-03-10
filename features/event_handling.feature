
Feature: Event Handling and Notifications

  Scenario: Listening for database events
    Given a running event listener
    When a new event "OrderCreated" is added to the event stream
    Then the listener should receive a notification
    And the listener should process the "OrderCreated" event

  Scenario: Handling concurrent stream writes
    Given an event store with an existing order
    When another event is appended with an outdated version
    Then a ConcurrentStreamWriteError should be raised
