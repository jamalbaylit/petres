@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=uv run sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build
set APIDIR=source\api

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

REM Special handling for clean
if "%1" == "clean" (
	echo Removing build directory...
	if exist %BUILDDIR% rmdir /s /q %BUILDDIR%
	echo Removing generated API documentation...
	if exist %APIDIR% rmdir /s /q %APIDIR%
	echo Clean complete.
	goto end
)

REM Special handling for html - clean before building
if "%1" == "html" (
	echo Cleaning previous build and generated files...
	if exist %BUILDDIR% rmdir /s /q %BUILDDIR%
	if exist %APIDIR% rmdir /s /q %APIDIR%
	echo Building HTML documentation...
	%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
	goto end
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
