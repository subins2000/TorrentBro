# Debian Packaging

`man` folder has the manual pages

## Updating From Upstream

* Download `.tar.gz` from upstream as `torrentbro_version.orig.tar.gz`
* Place the tar file outside current debian package folder
* Enter into the debian package folder and do :
  ```
  uupdate -v version ../torrentbro_version.orig.tar.gz
  ```
* Enter the new folder and package
```
  cd ../torrentbro_version
  ```
