# Understand the project

Browser = frontend. Flask = backend. MySQL = persistent storage.

Save reads the form in JavaScript and POSTs JSON. Flask validates it, INSERTs parameterized values, commits, and returns the stored record with 201. The browser refreshes using GET.

GET all returns an array; GET with ID returns an object or 404. PUT replaces every editable field. Close/Reopen fetches the latest record and PUTs the opposite status. DELETE removes a row. MySQL assigns IDs.

Frontend validation gives quick feedback. Backend validation protects against clients bypassing the form. It checks text lengths, positive integer positions, valid dates, status and unknown fields. Malformed JSON returns 400.

Parameterized queries separate SQL commands from user values. Rendering with textContent displays HTML-like input as text. Transactions commit writes together. PUT/DELETE lock the row during modification, and unchanged PUTs still succeed.

The assignment does not require login or student application submission. This local app focuses on faculty CRUD management. Before presenting, trace each operation from browser through API to database and explain 200, 201, 400, 404 and 500.
