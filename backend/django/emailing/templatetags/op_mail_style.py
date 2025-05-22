
from django                     import template
from django.template            import Template
from django.utils.safestring    import mark_safe
from django.utils.html          import escape as html_escape

from django.conf                import settings

register = template.Library()

"""
Some help here
https://docs.djangoproject.com/fr/1.8/howto/custom-template-tags/
http://www.djangobook.com/en/2.0/chapter09.html
"""

@register.inclusion_tag('emailing/templatetags/separator.html')
def op_separator():
    pass

@register.inclusion_tag('emailing/templatetags/banner.html')
def op_banner():
    pass

def op_container(parser, token):
    try:
        tag_name = token.split_contents()[0]
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires no arguments" % token.contents.split()[0]
        )
    nodelist = parser.parse(('op_container_end',))
    parser.delete_first_token()
    return ContainerNode(nodelist)

class ContainerNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
        # self.position = position
        # self.width = width

    def render(self, context):
        output = self.nodelist.render(context)
        return """
        <!-- OP_CONTAINER -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
            <tbody class="mcnTextBlockOuter">
                <tr>
                    <td valign="top" class="mcnTextBlockInner" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                        <div class="mcnTextContent" style="padding: 15px;color: #606060;font-family: Helvetica;font-size: 15px;line-height: 150%;text-align: justify;">
                            {content}
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        """.format(content = output)

@register.inclusion_tag('emailing/templatetags/social.html')
def op_social():
    pass

@register.inclusion_tag('emailing/templatetags/footer.html')
def op_footer():
    pass

def op_button(parser, token):
    args = token.contents.split()
    if len(args) < 2:
        raise template.TemplateSyntaxError(
            "%r tag requires at least 1 argument" % token.contents.split()[0]
        )
    if len(args[1]) and args[1][0] != '/':
        raise template.TemplateSyntaxError(
            "op_button urls must start with /"
        )

    tag_name = args[0]
    assert args[1] != '{', "Don't put space in the URL ! (got %s)" % args[1]
    img = None
    is_secure = False
    if len(args) >= 3:
        # The second argument may be :
        # - An image url, for image buttons
        # - the "secure" keyword, to indicate a secure url
        if args[2] == 'secure':
            is_secure = True
        else:
            img = args[2]

    if is_secure:
        href = settings.ANGULAR_APP_BASE_URL + args[1]
    else:
        href = settings.APP_BASE_URL + args[1]

    nodelist = parser.parse(('op_button_end',))
    parser.delete_first_token()
    return ButtonNode(nodelist, href, img)

def op_main_action_button(parser, token):
    res = op_button(parser, token)
    res.bg_color = "#228822"
    res.color = "white"
    return res


class ButtonNode(template.Node):
    def __init__(self, nodelist, href, img=None):
        """
        """
        self.nodelist       = nodelist
        self.href           = href
        self.bg_color       = "#EEEEEE"
        self.color          = "#666666"
        self.img            = img

    def render(self, context):
        # Rendering href (because variable arguments aren't interpreted by default)
        href = Template(self.href).render(context)
        # Rendering content between beacons
        output = self.nodelist.render(context)
        style = "display: block; padding-bottom: 10px; padding-top: 10px; text-align: center; border-radius: 10px;"
        style += ";color:%s" % self.color
        if self.img is not None:
            style += ";padding-left: 30px; background: url(%s) no-repeat %s" % (self.img, self.bg_color)
            style += ";background-position: 40px center"
        else:
            style += ";background-color: %s" % self.bg_color

        res = """
        <!-- OP_BUTTON -->
        <a href="{href}" target="_blank" class="op-btn" style="{style}">
                {content}
        </a>
        """.format(content=output, href=mark_safe(href), style=style)
        return res

def op_column(parser, token):
    try:
        tag_name, position, width = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly 2 arguments" % token.contents.split()[0]
        )
    nodelist = parser.parse(('op_column_end',))
    parser.delete_first_token()
    return ColumnNode(nodelist, position, width)

class ColumnNode(template.Node):
    def __init__(self, nodelist, position, width):
        self.nodelist = nodelist
        self.position = position
        self.width = width

    def render(self, context):
        output = self.nodelist.render(context)
        return """
        <!-- OP_COLUMN -->
        <table align="{align}" border="0" cellpadding="0" cellspacing="0" width="{width}" class="mcnTextContentContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
            <tbody>
                <tr>
                    <td valign="top" class="mcnTextContent" style="padding: 0px !important;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;color: #606060;font-family: Helvetica;font-size: 15px;line-height: 150%;text-align: left;">
                        {content}
                    </td>
                </tr>
            </tbody>
        </table>
        """.format(align = self.position, width = self.width, content = output)


@register.simple_tag
def cms_url(url):
    if len(url) and url[0] != '/':
        raise Exception("front_url urls must start with /")
    return mark_safe(settings.CMS_BASE_URL + url)

class AppUrlNode(template.Node):
    def __init__(self, url):
        self.url = url

    def render(self, context):
        url = Template(self.url).render(context)
        return mark_safe(url)

def app_url(parser, token):
    args = token.contents.split()
    url = args[1]
    if len(url) and url[0] != '/':
        raise Exception("front_url urls must start with / : %s" % url)
    return AppUrlNode(settings.APP_BASE_URL + url)

@register.simple_tag
def app_url_secure(url):
    if len(url) and url[0] != '/':
        raise Exception("front_url_secure urls must start with /")
    return mark_safe(settings.ANGULAR_APP_BASE_URL + url)

@register.simple_tag
def brand_name():
    return html_escape(settings.APP_BRAND_NAME)

@register.simple_tag
def support_email():
    return settings.SUPPORT_EMAIL

register.tag('op_container', op_container)
register.tag('op_button', op_button)
register.tag('app_url', app_url)
register.tag('op_main_action_button', op_main_action_button)
register.tag('op_column', op_column)