Installation with Git / Anaconda
--------------------------------

.. code-block:: console

    # Clone repository
    $ git clone https://github.com/garciafido/cima-goes-examples.git
    $ cd cima-goes-examples

.. code-block:: console

    # Install library
    $ conda create -n cima-goes-examples python=3.8
    $ conda activate cima-goes-examples
    $ conda install -c conda-forge cartopy
    $ pip install cima.goes

.. code-block:: console

    # Run some examples
    $ python 01_blob_to_netcdf_file.py
    $ python 03_clipping_to_netcdf_file.py
    $ python 04_clipping_to_image_file.py

Obtaining GCP Credentials
-------------------------

https://cloud.google.com/docs/authentication/production#obtaining_and_providing_service_account_credentials_manually