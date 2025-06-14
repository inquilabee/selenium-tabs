# Test Coverage Documentation

## Overview
This document outlines the current test coverage for the `Tab` class in the `seleniumtabs` package. It identifies which functionalities are currently tested and which areas need additional test coverage.

## Currently Tested Functionalities

### Basic Tab Operations
- Opening new tabs
- Closing tabs
- Switching between tabs
- Tab state management (active/alive)

### Scrolling Operations
- Basic scrolling
- Scroll up/down
- Scroll to bottom
- Infinite scroll

### Tab Properties
- Title
- URL
- Active state
- Alive state
- Page source

## Areas Needing Test Coverage

### 1. CSS Selector Methods
- `css()` method
- `SelectableCSS` functionality

### 2. JavaScript Operations
- `run_js()` method
- `get_all_attributes_of_element()`
- `get_attribute()`

### 3. Element Interaction Methods
- `click()` and `_click_on_random_position()`
- `empty_click()`
- `element_source()`
- `element_location()`
- `element_size()`
- `element_center()`

### 4. Element Finding and Waiting
- `find_element()`
- `wait_for_presence_of_element()`
- `wait_for_visibility_of_element()`
- `wait_for_presence_and_visibility_of_element()`
- `wait_for_presence()`
- `wait_for_visibility()`
- `wait_for_presence_and_visibility()`
- `wait_for_body_tag_presence_and_visibility()`
- `wait_until_staleness()`
- `wait_for_url()`

### 5. jQuery/PyQuery Integration
- `jquery` and `jq` properties
- `pyquery` and `pq` properties
- `page_html` property

### 6. Task Scheduling
- `schedule_task()` method

### 7. Page State Methods
- `has_page_loaded()`
- `wait_for_loading()`

### 8. URL and Domain Operations
- `domain` property
- `wait_for_url()`

## Test Implementation Priority

1. **High Priority**
   - CSS Selector methods (core functionality)
   - Element interaction methods (critical for automation)
   - Element finding and waiting (essential for reliable tests)

2. **Medium Priority**
   - JavaScript operations
   - jQuery/PyQuery integration
   - Page state methods

3. **Lower Priority**
   - Task scheduling
   - URL and domain operations

## Notes
- Current tests are primarily focused on basic tab operations and scrolling
- Many core functionalities remain untested
- Test implementation should follow the priority order to ensure critical features are covered first
- Each new test should include both positive and negative test cases
- Edge cases should be considered for each functionality 