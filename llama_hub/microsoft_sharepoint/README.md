# Microsoft SharePoint Reader

The loader loads the files from a folder in sharepoint site.

It also supports traversing recursively through the sub-folders.

## Prequsites

### App Authentication using Microsoft Entra ID(formerly Azure AD)

1. You need to create an App Registeration in Microsoft Entra ID. Refer [here](https://learn.microsoft.com/en-us/azure/healthcare-apis/register-application)
2. API Permissions for the created app.
   1. Micorsoft Graph --> Application Permissions --> Sites.ReadAll (**Grant Admin Consent**)
   2. Microsoft Graph --> Application Permissions --> Files.ReadAll (**Grant Admin Consent**)
   3. Microsoft Graph --> Application Permissions --> BrowserSiteLists.Read.All (**Grant Admin Consent**)

More info on Microsoft Graph APIs - [Refer here](https://learn.microsoft.com/en-us/graph/permissions-reference)

## Usage

To use this loader `client_id`, `client_secret` and `tenant_id` of the registered app in Microsoft Azure Portal is required.

This loader loads the files present in a specific folder in sharepoint.

If the files are present in the `Test` folder in SharePoint Site under `root` directory, then the input for the loader for  `file_path` is `Test`

![FilePath](file_path_info.png)

```python
from llama_index import download_loader 
SharePointLoader = download_loader("SharePointReader")

loader = SharePointLoader(
            client_id = "<Client ID of the app>",
            client_secret = "<Client Secret of the app>",
            tenant_id = "<Tenant ID of the Micorsoft Azure Directory>"
            )

documents = loader.load_data(
            sharepoint_site_name: "<Sharepoint Site Name>",
            sharepoint_folder_path: "<Folder Path>",
            recursive = True,
)
```

The loader doesn't access other components of the `SharePoint Site`.

