# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language_from_request
from meta import settings as meta_settings


def get_cache_key(page, language):
    """
    Create the cache key for the current page and language
    """
    from cms.cache import _get_cache_key
    site_id = page.site_id
    return _get_cache_key('page_meta', page, language, site_id)


def get_page_meta(page, language):
    """
    Retrieves all the meta information for the page in the given language

    :param page: a Page instance
    :param lang: a language code

    :return: Meta instance
    :type: object
    """
    from django.core.cache import cache
    from meta.views import Meta
    from .models import PageMeta, TitleMeta

    try:
        meta_key = get_cache_key(page, language)
    except AttributeError:
        return None
    gplus_server = 'https://plus.google.com'
    titlemeta = None
    meta = cache.get(meta_key)
    if not meta:
        meta = Meta()
        title = page.get_title_obj(language)
        meta.extra_custom_props = []

        meta.title = page.get_page_title(language)
        if not meta.title:
            meta.title = page.get_title(language)

        if title.meta_description:
            meta.description = title.meta_description.strip()
        try:
            titlemeta = title.titlemeta
            if titlemeta.description:
                meta.description = titlemeta.description.strip()
            if titlemeta.keywords:
                meta.keywords = titlemeta.keywords.strip().split(',')
            meta.locale = titlemeta.locale
            meta.og_description = titlemeta.og_description.strip()
            meta.twitter_description = titlemeta.twitter_description.strip()
            meta.gplus_description = titlemeta.gplus_description.strip()
            if titlemeta.image:
                meta.image = title.titlemeta.image.canonical_url or title.titlemeta.image.url
            for item in titlemeta.extra.all():
                attribute = item.attribute
                if not attribute:
                    attribute = item.DEFAULT_ATTRIBUTE
                meta.extra_custom_props.append((attribute, item.name, item.value))
        except (TitleMeta.DoesNotExist, AttributeError):
            # Skipping title-level metas
            pass
        defaults = {
            'object_type': meta_settings.FB_TYPE,
            'og_type': meta_settings.FB_TYPE,
            'og_app_id': meta_settings.FB_APPID,
            'fb_pages': meta_settings.FB_PAGES,
            'og_profile_id': meta_settings.FB_PROFILE_ID,
            'og_publisher': meta_settings.FB_PUBLISHER,
            'og_author_url': meta_settings.FB_AUTHOR_URL,
            'twitter_type': meta_settings.TWITTER_TYPE,
            'twitter_site': meta_settings.TWITTER_SITE,
            'twitter_author': meta_settings.TWITTER_AUTHOR,
            'gplus_type': meta_settings.GPLUS_TYPE,
            'gplus_author': meta_settings.GPLUS_AUTHOR,
        }
        try:
            pagemeta = page.pagemeta
            meta.object_type = pagemeta.og_type
            meta.og_type = pagemeta.og_type
            meta.og_app_id = pagemeta.og_app_id
            meta.fb_pages = pagemeta.fb_pages
            meta.og_profile_id = pagemeta.og_author_fbid
            meta.twitter_type = pagemeta.twitter_type
            meta.twitter_site = pagemeta.twitter_site
            meta.twitter_author = pagemeta.twitter_author
            meta.gplus_type = pagemeta.gplus_type
            meta.gplus_author = pagemeta.gplus_author
            if not meta.gplus_author.startswith('http'):
                if not meta.gplus_author.startswith('/'):
                    meta.gplus_author = '{0}/{1}'.format(gplus_server, meta.gplus_author)
                else:
                    meta.gplus_author = '{0}{1}'.format(gplus_server, meta.gplus_author)
            if page.publication_date:
                meta.published_time = page.publication_date.isoformat()
            if page.changed_date:
                meta.modified_time = page.changed_date.isoformat()
            if page.publication_end_date:
                meta.expiration_time = page.publication_end_date.isoformat()
            if meta.og_type == 'article':
                meta.og_publisher = pagemeta.og_publisher
                meta.og_author_url = pagemeta.og_author_url
                try:
                    from djangocms_page_tags.utils import get_title_tags, get_page_tags
                    tags = list(get_title_tags(page, language))
                    tags += list(get_page_tags(page))
                    meta.tag = ','.join([tag.name for tag in tags])
                except ImportError:
                    # djangocms-page-tags not available
                    pass
            if not meta.image and pagemeta.image:
                meta.image = pagemeta.image.canonical_url or pagemeta.image.url
            # added page level fields
            if pagemeta.title:
                meta.title = pagemeta.title
            # we can override the meta description defined on the page
            # otherwise we only update if there isn't a title description already
            if pagemeta.description and (not titlemeta or (titlemeta and not titlemeta.description)):
                meta.description = pagemeta.description
            if pagemeta.og_description and (not getattr(meta, 'og_description', '') or (titlemeta and not titlemeta.og_description)):
                meta.og_description = pagemeta.og_description
            if pagemeta.twitter_description and (not getattr(meta, 'twitter_description', '') or (titlemeta and not titlemeta.twitter_description)):
                meta.twitter_description = pagemeta.twitter_description
            if pagemeta.gplus_description and (not getattr(meta, 'gplus_description', '') or (titlemeta and not titlemeta.gplus_description)):
                meta.gplus_description = pagemeta.gplus_description
            if not meta.keywords and pagemeta.keywords:
                meta.keywords = pagemeta.keywords.strip().split(',')

            for item in pagemeta.extra.all():
                attribute = item.attribute
                if not attribute:
                    attribute = item.DEFAULT_ATTRIBUTE
                meta.extra_custom_props.append((attribute, item.name, item.value))
        except PageMeta.DoesNotExist:
            pass

        # override social descriptions with the general
        # descriptions if nothing more specific was found
        if meta.description:
            if not getattr(meta,'og_description', ''):
                meta.og_description = meta.description
            if not getattr(meta,'twitter_description', ''):
                meta.twitter_description = meta.description
            if not getattr(meta,'gplus_description', ''):
                meta.gplus_description = meta.description

        for attr, val in defaults.items():
            if not getattr(meta, attr, '') and val:
                setattr(meta, attr, val)
        meta.url = page.get_absolute_url(language)
    return meta


def get_metatags(request):
    language = get_language_from_request(request, check_path=True)
    meta = get_page_meta(request.current_page, language)
    return mark_safe(
        render_to_string(
            request=request,
            template_name='djangocms_page_meta/meta.html',
            context={'meta': meta}
        )
    )
