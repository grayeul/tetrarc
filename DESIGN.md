These are design notes for a Playbook Replacement for Rocky testing.

This is based largely on looking at example web pages from 'OnBelay' -- here: https://claude.ai/public/artifacts/be89e003-f857-4ef8-b7cf-f9bc8fd472e1

I am thinking about doing a Rio based web-paged, with info managed via a database.
Here are some thoughts on the database layout/table info

BasicTests:   (basic definition of tests that could be run)
  name
  shortname
  testgroup
  testorder (for sorting within group)
  description
  last_updated
  link_to_procedure
  last_modified_by

TestEvents:  (instances of tests to-be-run, or have-been-run)
  basicTest
  architecture
  test_environ
  claimant

TestResults
  TestEvent
  username
  status (pass/fail/partial)
  comments
  submitted_date

TestBook  (Name of overall release)
  name
  start_date
  target_end_date
  status  (open/closed/prep)


=============================================================
Now look at the presentation side -- which pages, and what content should be:

MainPage: (after login)
  Banner with summary of purpose
  Button to go to Past/Closed Results page
  Cards with ongoing tests -- has summary of status
    clicking takes you to main TestBook page for given test

TestBookPage
  link to get back to main page
  summary info for this testbook
     (includes num tests, num passing, etc)
  buttons to download results in several format?( json/markdown)
  grid with detailed results and following columns:
    TestName   Architecture  Pass/Fail  User  TestEnv  SubmissionTime  (link for comments?)

  Need ability to filter or sort table by architecture/pass/fail/etc...


