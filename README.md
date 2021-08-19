# Nix Python demo

This is an example web application / API server in Python that uses Nix for
it's development environment. The application itself does not do much, but I
spent some time making the development environment pretty nice.

Made this for a presentation at Iterative.

## Technologies used

Core to the workflow are:

 - Nix - https://nixos.org/
 - Direnv - https://direnv.net/

Together, I have found these two to be really powerful. If you're working in
a team, these will be the only tools that need to be installed on your colleagues
machines to get started developing.

Running the application is as simple as:

 - Installing Nix and `direnv`
 - Cloning the repository
 - Running `direnv allow`
 - Running the `start` command

After you have these two, you can build anything yourself, as demonstrated
here. I took a mostly from scratch approach in a few places just because I
thought that was fun. There is nothing stopping you from incorporating more
established patterns though.

This repository contains:

 - Postgres 13 for data storage.
 - A DIY migration tool.
 - DIY pre-commit script.
 - Some basic testing.

You probably already have some preferences / weapons of choice here.
