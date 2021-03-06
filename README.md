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

## Testimonials

 - At [Channable][channable-nix] (disclaimer: used to work on this). ([HN
   discussion][channable-nix-hn])
 - At [Shopify][shopify-nix] ([HN discussion][shopify-nix-hn])
 - HashiCorp uses Nix for [Waypoint][hashicorp-waypoint]

[channable-nix]:https://www.channable.com/tech/nix-is-the-ultimate-devops-toolkit
[channable-nix-hn]:https://news.ycombinator.com/item?id=26748696
[shopify-nix]:https://shopify.engineering/what-is-nix
[shopify-nix-hn]:https://news.ycombinator.com/item?id=23251754
[hashicorp-waypoint]:https://github.com/hashicorp/waypoint

## Resources

 - https://nix.dev/
 - https://nixos.wiki/
