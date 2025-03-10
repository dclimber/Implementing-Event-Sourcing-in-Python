
Feature: Postgres Integration

  Scenario: Storing and retrieving events from PostgreSQL
    Given a PostgreSQL database
    When events are stored in the database
    Then the events should be retrievable from the database
    And the version of the event stream should match the number of stored events
