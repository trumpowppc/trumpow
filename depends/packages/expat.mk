package=expat
$(package)_version=2.5.0
# disable to test
# $(package)_download_path=https://github.com/libexpat/libexpat/releases/download/R_2_5_0/
# $(package)_file_name=$(package)-$($(package)_version).tar.bz2
# $(package)_sha256_hash=6f0e6e01f7b30025fa05c85fdad1e5d0ec7fd35d9f61b22f34998de11969ff67

# define $(package)_set_vars
#   $(package)_config_opts=--disable-shared --without-docbook --without-tests --without-examples
#   $(package)_config_opts += --disable-dependency-tracking --enable-option-checking
#   $(package)_config_opts_linux=--with-pic
# endef

# test using this source
$(package)_download_path=https://downloads.sourceforge.net/project/expat/expat/$($(package)_version)
$(package)_file_name=$(package)-$($(package)_version).tar.bz2
$(package)_sha256_hash=6f0e6e01f7b30025fa05c85fdad1e5d0ec7fd35d9f61b22f34998de11969ff67

define $(package)_set_vars
  $(package)_config_opts=--disable-shared --without-docbook --without-tests --without-examples
  $(package)_config_opts += --disable-dependency-tracking --enable-option-checking
  $(package)_config_opts_linux=--with-pic
endef

define $(package)_config_cmds
  $($(package)_autoconf)
endef

define $(package)_build_cmds
  $(MAKE)
endef

define $(package)_stage_cmds
  $(MAKE) DESTDIR=$($(package)_staging_dir) install
endef

define $(package)_postprocess_cmds
  rm -rf share lib/cmake lib/*.la
endef