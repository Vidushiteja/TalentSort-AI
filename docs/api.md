# API quick reference

Interactive OpenAPI docs: `/docs`

- `GET /api/health`
- `GET /api/dashboard`
- `POST /api/jobs`, `GET /api/jobs`, `GET /api/jobs/{id}`, `PUT /api/jobs/{id}`
- `PATCH /api/jobs/{id}/archive?archived=true`, `DELETE /api/jobs/{id}`
- `POST /api/jobs/{id}/resumes` (multipart field `files`, repeated)
- `GET /api/jobs/{id}/results?search=&decision=&sort=score&order=desc&page=1&page_size=20`
- `GET /api/results/{id}`, `POST /api/results/{id}/rescreen`
- `GET /api/jobs/{id}/compare?ids=1,2`
- `PATCH /api/resumes/{id}/decision`
- `POST/GET /api/resumes/{id}/notes`
- `GET /api/resumes/{id}/history`
- `DELETE /api/resumes/{id}`
