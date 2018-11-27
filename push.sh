#!/bin/sh

setup_git() {
	git config --global user.email "travis@travis-ci.org"
	git config --global user.name "Travis CI"
	git remote rm origin
	git remote add origin https://${GH_TOKEN}@github.com/kcsluis/kcsluis.github.io
}

commit_files() {
	git checkout master
	git add . *.tsv
	git commit --message "Travis build: $TRAVIS_BUILD_NUMBER"
}

upload_files() {
	git push -u origin master 
}

setup_git
commit_files
upload_files
