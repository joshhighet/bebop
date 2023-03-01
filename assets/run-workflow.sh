#!/bin/bash
gh workflow run bebop.yml --repo joshhighet/bebop
gh run list --workflow=bebop.yml --repo joshhighet/bebop