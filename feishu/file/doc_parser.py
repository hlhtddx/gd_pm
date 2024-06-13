import json
import typing
from copy import deepcopy
from typing import List


@attr.s
class DocItem(object):
    def parse(self, parser, param):
        new_item = parser(self, param)
        return new_item

    @staticmethod
    def default_parser(item, parser, param):
        cls = item.__class__
        initializer = {}
        for field in attr.fields(cls):
            new_attr = getattr(item, field.name, field.default)
            if isinstance(new_attr, DocItem):
                initializer[field.name] = parser(new_attr, param)
            elif isinstance(new_attr, list):
                initializer[field.name] = [parser(i, param) for i in new_attr]
            elif isinstance(new_attr, (str, int, float)):
                initializer[field.name] = deepcopy(new_attr)
            elif new_attr is None:
                initializer[field.name] = new_attr
            else:
                raise TypeError(new_attr.__class__)
        return cls(**initializer)


@to_json_decorator
@attr.s
class Location(DocItem):
    zone_id = attr.ib(type=str, default=None, metadata={'json': 'zoneId'})
    start_index = attr.ib(type=int, default=None, metadata={'json': 'startIndex'})
    end_index = attr.ib(type=int, default=None, metadata={'json': 'endIndex'})


@to_json_decorator
@attr.s
class RGBColor(DocItem):
    red = attr.ib(type=int, default=None, metadata={'json': 'red'})
    green = attr.ib(type=int, default=None, metadata={'json': 'green'})
    blue = attr.ib(type=int, default=None, metadata={'json': 'blue'})
    alpha = attr.ib(type=float, default=None, metadata={'json': 'alpha'})


@to_json_decorator
@attr.s(auto_attribs=True)
class Body(DocItem):
    # blocks: typing.List['Block'] = attr.ib(type=typing.List['Block'], default=None, metadata={'json': 'blocks'})
    blocks: typing.List['Block'] = attr.ib(default=None, metadata={'json': 'blocks'})


@to_json_decorator
@attr.s
class UndefinedBlock(DocItem):
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class DocsApp(DocItem):
    type_id = attr.ib(type=str, default=None, metadata={'json': 'typeId'})
    instance_id = attr.ib(type=str, default=None, metadata={'json': 'instanceId'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Callout(DocItem):
    callout_emoji_id = attr.ib(type=str, default=None, metadata={'json': 'calloutEmojiId'})
    callout_background_color = attr.ib(type=RGBColor, default=None, metadata={'json': 'calloutBackgroundColor'})
    callout_border_color = attr.ib(type=RGBColor, default=None, metadata={'json': 'calloutBorderColor'})
    callout_text_color = attr.ib(type=RGBColor, default=None, metadata={'json': 'CalloutTextColor'})
    body = attr.ib(type=Body, default=None, metadata={'json': 'body'})
    zone_id = attr.ib(type=str, default=None, metadata={'json': 'zoneId'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Code(DocItem):
    language = attr.ib(type=str, default=None, metadata={'json': 'language'})
    wrap_content = attr.ib(type=bool, default=None, metadata={'json': 'wrapContent'})
    body = attr.ib(type=Body, default=None, metadata={'json': 'body'})
    zone_id = attr.ib(type=str, default=None, metadata={'json': 'zoneId'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Poll(DocItem):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Jira(DocItem):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    jira_type = attr.ib(type=str, default=None, metadata={'json': 'jiraType'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Diagram(DocItem):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    diagram_type = attr.ib(type=str, default=None, metadata={'json': 'diagramType'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Bitable(DocItem):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    view_type = attr.ib(type=str, default=None, metadata={'json': 'viewType'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Sheet(DocItem):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    row_size = attr.ib(type=int, default=None, metadata={'json': 'rowSize'})
    column_size = attr.ib(type=int, default=None, metadata={'json': 'columnSize'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class MergedCell(DocItem):
    merged_cell_id = attr.ib(type=str, default=None, metadata={'json': 'mergedCellId'})
    row_start_index = attr.ib(type=int, default=None, metadata={'json': 'rowStartIndex'})
    row_end_index = attr.ib(type=int, default=None, metadata={'json': 'rowEndIndex'})
    column_start_index = attr.ib(type=int, default=None, metadata={'json': 'columnStartIndex'})
    column_end_index = attr.ib(type=int, default=None, metadata={'json': 'columnEndIndex'})


@to_json_decorator
@attr.s
class TableColumnProperties(DocItem):
    width = attr.ib(type=int, default=None, metadata={'json': 'width'})


@to_json_decorator
@attr.s
class TableStyle(DocItem):
    table_column_properties = attr.ib(type=List[TableColumnProperties], default=None,
                                      metadata={'json': 'tableColumnProperties'})


@to_json_decorator
@attr.s
class TableCell(DocItem):
    column_index = attr.ib(type=int, default=None, metadata={'json': 'columnIndex'})
    zone_id = attr.ib(type=str, default=None, metadata={'json': 'zoneId'})
    body = attr.ib(type=Body, default=None, metadata={'json': 'body'})


@to_json_decorator
@attr.s
class TableRow(DocItem):
    row_index = attr.ib(type=int, default=None, metadata={'json': 'rowIndex'})
    table_cells = attr.ib(type=List[TableCell], default=None, metadata={'json': 'tableCells'})


@to_json_decorator
@attr.s
class Table(DocItem):
    table_id = attr.ib(type=str, default=None, metadata={'json': 'tableId'})
    row_size = attr.ib(type=int, default=None, metadata={'json': 'rowSize'})
    column_size = attr.ib(type=int, default=None, metadata={'json': 'columnSize'})
    table_rows = attr.ib(type=List[TableRow], default=None, metadata={'json': 'tableRows'})
    table_style = attr.ib(type=TableStyle, default=None, metadata={'json': 'tableStyle'})
    merged_cells = attr.ib(type=List[MergedCell], default=None, metadata={'json': 'mergedCells'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class ChatGroup(DocItem):
    open_chat_id = attr.ib(type=str, default=None, metadata={'json': 'openChatId'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class EmbeddedPage(DocItem):
    type = attr.ib(type=str, default=None, metadata={'json': 'type'})
    url = attr.ib(type=str, default=None, metadata={'json': 'url'})
    width = attr.ib(type=float, default=None, metadata={'json': 'width'})
    height = attr.ib(type=float, default=None, metadata={'json': 'height'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class HorizontalLine(DocItem):
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class File(DocItem):
    file_token = attr.ib(type=str, default=None, metadata={'json': 'fileToken'})
    view_type = attr.ib(type=str, default=None, metadata={'json': 'viewType'})
    file_name = attr.ib(type=str, default=None, metadata={'json': 'fileName'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class ImageItem(DocItem):
    file_token = attr.ib(type=str, default=None, metadata={'json': 'fileToken'})
    width = attr.ib(type=float, default=None, metadata={'json': 'width'})
    height = attr.ib(type=float, default=None, metadata={'json': 'height'})


@to_json_decorator
@attr.s
class GalleryStyle(DocItem):
    align = attr.ib(type=str, default=None, metadata={'json': 'align'})


@to_json_decorator
@attr.s
class Gallery(DocItem):
    gallery_style = attr.ib(type=GalleryStyle, default=None, metadata={'json': 'galleryStyle'})
    image_list = attr.ib(type=List[ImageItem], default=None, metadata={'json': 'imageList'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class UndefinedElement(DocItem):
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Equation(DocItem):
    equation = attr.ib(type=str, default=None, metadata={'json': 'equation'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Reminder(DocItem):
    is_whole_day = attr.ib(type=bool, default=None, metadata={'json': 'isWholeDay'})
    timestamp = attr.ib(type=int, default=None, metadata={'json': 'timestamp'})
    should_notify = attr.ib(type=bool, default=None, metadata={'json': 'shouldNotify'})
    notify_type = attr.ib(type=int, default=None, metadata={'json': 'notifyType'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Person(DocItem):
    open_id = attr.ib(type=str, default=None, metadata={'json': 'openId'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class DocsLink(DocItem):
    url = attr.ib(type=str, default=None, metadata={'json': 'url'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class Link(DocItem):
    url = attr.ib(type=str, default=None, metadata={'json': 'url'})


@to_json_decorator
@attr.s
class TextStyle(DocItem):
    bold = attr.ib(type=bool, default=None, metadata={'json': 'bold'})
    italic = attr.ib(type=bool, default=None, metadata={'json': 'italic'})
    strike_through = attr.ib(type=bool, default=None, metadata={'json': 'strikeThrough'})
    underline = attr.ib(type=bool, default=None, metadata={'json': 'underline'})
    code_inline = attr.ib(type=bool, default=None, metadata={'json': 'codeInline'})
    back_color = attr.ib(type=RGBColor, default=None, metadata={'json': 'backColor'})
    text_color = attr.ib(type=RGBColor, default=None, metadata={'json': 'textColor'})
    link = attr.ib(type=Link, default=None, metadata={'json': 'link'})


@to_json_decorator
@attr.s
class TextRun(DocItem):
    text = attr.ib(type=str, default=None, metadata={'json': 'text'})
    style = attr.ib(type=TextStyle, default=None, metadata={'json': 'style'})
    line_id = attr.ib(type=str, default=None, metadata={'json': 'lineId'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})


@to_json_decorator
@attr.s
class ParagraphElement(DocItem):
    type = attr.ib(type=str, default=None, metadata={'json': 'type'})
    text_run = attr.ib(type=TextRun, default=None, metadata={'json': 'textRun'})
    docs_link = attr.ib(type=DocsLink, default=None, metadata={'json': 'docsLink'})
    person = attr.ib(type=Person, default=None, metadata={'json': 'person'})
    equation = attr.ib(type=Equation, default=None, metadata={'json': 'equation'})
    reminder = attr.ib(type=Reminder, default=None, metadata={'json': 'reminder'})
    file = attr.ib(type=File, default=None, metadata={'json': 'file'})
    jira = attr.ib(type=Jira, default=None, metadata={'json': 'jira'})
    undefined_element = attr.ib(type=UndefinedElement, default=None, metadata={'json': 'undefinedElement'})


@to_json_decorator
@attr.s
class List2(DocItem):
    type = attr.ib(type=str, default=None, metadata={'json': 'type'})
    indent_level = attr.ib(type=int, default=None, metadata={'json': 'indentLevel'})
    number = attr.ib(type=int, default=None, metadata={'json': 'number'})


@to_json_decorator
@attr.s
class ParagraphStyle(DocItem):
    heading_level = attr.ib(type=int, default=None, metadata={'json': 'headingLevel'})
    collapse = attr.ib(type=bool, default=None, metadata={'json': 'collapse'})
    list = attr.ib(type=List2, default=None, metadata={'json': 'list'})
    quote = attr.ib(type=bool, default=None, metadata={'json': 'quote'})
    align = attr.ib(type=str, default=None, metadata={'json': 'align'})


@to_json_decorator
@attr.s
class Paragraph(DocItem):
    style = attr.ib(type=ParagraphStyle, default=None, metadata={'json': 'style'})
    elements = attr.ib(type=List[ParagraphElement], default=None, metadata={'json': 'elements'})
    location = attr.ib(type=Location, default=None, metadata={'json': 'location'})
    line_id = attr.ib(type=str, default=None, metadata={'json': 'lineId'})


@to_json_decorator
@attr.s
class Block(DocItem):
    type = attr.ib(type=str, default=None, metadata={'json': 'type'})
    paragraph = attr.ib(type=Paragraph, default=None, metadata={'json': 'paragraph'})
    horizontal_line = attr.ib(type=HorizontalLine, default=None, metadata={'json': 'horizontalLine'})
    embedded_page = attr.ib(type=EmbeddedPage, default=None, metadata={'json': 'embeddedPage'})
    chat_group = attr.ib(type=ChatGroup, default=None, metadata={'json': 'chatGroup'})
    table = attr.ib(type=Table, default=None, metadata={'json': 'table'})
    sheet = attr.ib(type=Sheet, default=None, metadata={'json': 'sheet'})
    bitable = attr.ib(type=Bitable, default=None, metadata={'json': 'bitable'})
    gallery = attr.ib(type=Gallery, default=None, metadata={'json': 'gallery'})
    file = attr.ib(type=File, default=None, metadata={'json': 'file'})
    diagram = attr.ib(type=Diagram, default=None, metadata={'json': 'diagram'})
    jira = attr.ib(type=Jira, default=None, metadata={'json': 'jira'})
    poll = attr.ib(type=Poll, default=None, metadata={'json': 'poll'})
    code = attr.ib(type=Code, default=None, metadata={'json': 'code'})
    docs_app = attr.ib(type=DocsApp, default=None, metadata={'json': 'docsApp'})
    callout = attr.ib(type=Callout, default=None, metadata={'json': 'callout'})
    undefined_block = attr.ib(type=UndefinedBlock, default=None, metadata={'json': 'undefinedBlock'})


@to_json_decorator
@attr.s
class Document(DocItem):
    title = attr.ib(type=Paragraph, default=None, metadata={'json': 'title'})
    body = attr.ib(type=Body, default=None, metadata={'json': 'body'})


attr.resolve_types(Body, globals(), locals())


class DocParser:
    def __init__(self, content: str) -> None:
        self.document = make_datatype(Document, content)

    def to_json(self) -> str:
        return json.dumps(self.document.json(), ensure_ascii=False)

    @staticmethod
    def parser_for_upload(item, param):
        if isinstance(item, Location):
            return None
        if isinstance(item, Person):
            return None
        return DocItem.default_parser(item, DocParser.parse_for_upload, param)

    def parse_for_upload(self, param):
        new_doc = self.document.parse(DocParser.parse_for_upload, param)
        return new_doc

    def post_pull(self, parser, param):
        new_doc = self.document.parse(parser, param)
        return new_doc
