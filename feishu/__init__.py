# from feishu.auth import lark_call, LarkCallArguments

#
# @lark_call(ContactService)
# def user_get(args, user_id, user_id_type) -> UserGetResult:
#     return args.service.users.get(user_access_token=args.user_access_token). \
#         set_user_id(user_id).set_user_id_type(user_id_type).do()
#
#
# @lark_call(DriveExplorerService)
# def folder_root_meta(args) -> FolderRootMetaResult:
#     return args.service.folders.root_meta(user_access_token=args.user_access_token).do()
#
#
# @lark_call(DriveExplorerService)
# def folder_meta(args, token) -> FolderMetaResult:
#     return args.service.folders.meta(user_access_token=args.user_access_token).set_folderToken(token).do()
#
#
# @lark_call(DriveExplorerService)
# def folder_children(args, token) -> FolderChildrenResult:
#     return args.service.folders.children(user_access_token=args.user_access_token).set_folderToken(token).do()
#
#
# @lark_call(DriveExplorerService)
# def folder_create(args, body: FolderCreateReqBody, token) -> FolderCreateResult:
#     return args.service.folders.create(body=body, user_access_token=args.user_access_token).set_folderToken(token).do()
#
#
# @lark_call(DocService)
# def doc_meta(args, token) -> DocMetaResult:
#     return args.service.docs.meta(user_access_token=args.user_access_token).set_docToken(token).do()
#
#
# @lark_call(DocService)
# def doc_content(args, token) -> DocContentResult:
#     return args.service.docs.content(user_access_token=args.user_access_token).set_docToken(token).do()
#
#
# @lark_call(DocService)
# def doc_create(args, folder_token, content) -> DocCreateResult:
#     body = DocCreateReqBody(folder_token, content)
#     return args.service.docs.create(body=body, user_access_token=args.user_access_token).do()
#
#
# @lark_call(FileService)
# def file_download(args, token):
#     return args.service.files.download(user_access_token=args.user_access_token). \
#         set_file_token(token).do()
#
#
# @lark_call(MediaService)
# def media_download(args, token):
#     return args.service.medias.download(user_access_token=args.user_access_token). \
#         set_file_token(token).do()
#
#
# @lark_call(MediaService)
# def media_upload_all(args, file_name, parent_type, p_token, size, file):
#     return args.service.medias.upload_all(user_access_token=args.user_access_token). \
#         set_file_name(file_name).set_parent_type(parent_type). \
#         set_parent_node(p_token).set_size(size).set_folder(file).do()
