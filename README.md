# nippy

Video sharing software like YT

## Note
This project is a work in progress, use it for your own risk.

I'm changing the site stack for the time being, download the first commit version if you don't want to deal with this

## Features
- "Real time" video processing with FFMPEG with process percentage and queue using Huey
- Small software stack, using only PostgreSQL and Django on the backend for simplicity, requiring less resources
- Mobile friendly

## Instalation
set up docker container, execute and run these commands:

`docker exec -it {container_id} python manage.py makemigrations core && python manage.py migrate`

`docker exec -it {container_id} npm run build`

`docker exec -it {container_id} DJANGO_SUPPRESS_SYSTEM_CHECKS=django_vite.W001 python manage.py collectstatic`

## Development
`cd src`

`npm install`

`npm run dev` # run the vite server

`python manage.py makemigrations core && python manage.py migrate` # db migrations

`python manage.py runserver` # run dev server

## License
This project is licensed under the GNU Affero General Public License v3.0 or later.

The AGPL requires that any modifications or derivatives of this project, when distributed or made available to others, must also be licensed under the AGPL. This means that if you run this software on a server and provide access to users, you must also provide access to the source code.