import logging
import re
import requests
from atproto import (
    Client,
    client_utils,
    models as atproto_models,
)
from bs4 import BeautifulSoup
from io import BytesIO
from pathlib import Path
from PIL import Image
# from django.conf import settings
from base.methods import (
    count_emoji,
    get_active_accounts,
    get_domain,
    message,
)
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
# DEFAULT_VISIBILITY = getattr(settings, "DEFAULT_VISIBILITY")


#====================UTILS: GET CONTENT METADATA====================#
def get_content_md(url):
    # fetch the page content
    response = requests.get(url)
    if response.status_code != 200: return None
    # parse the page content
    soup = BeautifulSoup(response.content, "html.parser")
    # extract metadata
    description = soup.find("meta", property="og:description")
    thumbnail = soup.find("meta", property="og:image")
    title = soup.find("meta", property="og:title")
    # return metadata
    return dict(
        description=description["content"] if description else None,
        thumbnail=thumbnail["content"] if thumbnail else None,
        title=title["content"] if title else None,
    )


#====================UTILS: VALIDATE IMAGE SIZE====================#
def validate_image_size(image_binary, **kwargs):
    factor = kwargs.get("factor", 0.5)
    limit = kwargs.get("limit", 999997)
    quality = kwargs.get("quality", 50)
    # return original image if no binary data or within size limit
    if not image_binary or len(image_binary) < limit:
        return image_binary
    # load the image from binary data
    image = Image.open(BytesIO(image_binary))
    # downsize the image
    resized_image = image.resize((int(image.width * factor), int(image.height * factor)))
    # save the resized image to a BytesIO object
    resized_image.save(output := BytesIO(), format=image.format, quality=quality, optimize=True)
    # return the resized image binary if within size limit
    return resized_binary if len(resized_binary := output.getvalue()) < limit else None


#====================BLUESKY: INSTANTIATE====================#
def instantiate(access_token, account_id):
    if not (access_token and account_id):
        log_message = message("LOG_EVENT", event="Bluesky not configured to be instantiated")
        logger.warning(log_message)
        return
    client = Client()
    login = client.login(
        account_id,
        Path(access_token).read_text().strip(),
    )
    return client


#====================BLUESKY: CLEAN VISIBILITY====================#
# NOTE: post visibility not currently supported on bluesky
# def clean_visibility(visibility, **kwargs):
#     default_visibility = kwargs.get("default_visibility", DEFAULT_VISIBILITY)
#     if visibility and visibility.lower() in ["public", "unlisted", "private", "direct"]:
#         return visibility.lower()
#     else:
#         return default_visibility.lower()


#====================BLUESKY: PREPARE POST====================#
def prepare_post(title, tags, link, **kwargs):
    embed_only = kwargs.get("embed_only", False)
    # set character limits
    char_limit = 300
    link_limit = sum((23, 2)) # additional 2 for newlines
    # count characters
    title_count = len(title)
    tags_count = len(tags)
    link_count = 0 if embed_only or not link else (link_limit if sum((len(link), 2)) > link_limit else sum((len(link), 2)))
    emoji_count, emoji_length = count_emoji(title + tags + link)
    # prioritise removing tags, then limiting title to accommodate link
    if sum((title_count, tags_count, link_count, emoji_count - emoji_length)) > char_limit:
        tags = ""
        emoji_count = count_emoji(title + tags + link)[0]
        title = title[:char_limit - (link_count + emoji_count)]
    # return post content
    return message(
        "FEED_POST",
        title=title,
        tags=tags,
        link=link if embed_only or not link else "\n\n%s" % link,
    )


#====================BLUESKY: BUILD RICH POST====================#
def build_rich_post(client, text, **kwargs):
    embed_only = kwargs.get("embed_only", False)
    link_embed = None
    rich_post = client_utils.TextBuilder()
    # define patterns
    hashtag_pattern = r"#\w+"
    mention_pattern = r"@\w+"
    url_pattern = r"http[s]?://\S+"
    # split the text using urls and keep the delimiters
    parts = re.split("(%s)" % url_pattern, text)
    # build rich post
    for part in parts:
        # build link
        if re.match(url_pattern, part):
            if not embed_only:
                rich_post.link(part, part)
            # skip creating link embed object if one exists
            if link_embed:
                continue
            # get required metadata
            link_metadata = get_content_md(part)
            # create link embed object if sufficient metadata
            if link_metadata and ((description := link_metadata.get("description")) and (title := link_metadata.get("title"))):
                thumbnail_bin = getattr(requests.get(thumbnail), "content", None) if (thumbnail := link_metadata.get("thumbnail")) else None
                params = dict(
                    description=description,
                    thumb=client.upload_blob(data=thumbnail_bin).blob if thumbnail_bin else None,
                    title=title,
                    uri=part,
                )
                link_embed = atproto_models.AppBskyEmbedExternal.Main(
                    external=atproto_models.AppBskyEmbedExternal.External(**params)
                )
        else:
            # split by spaces to handle individual words and hashtags - keep the spaces as separate elements
            words = re.split(r'(\s+)', part)
            for word in words:
                # build hashtag
                if re.match(hashtag_pattern, word):
                    rich_post.tag(word, word[1:])
                # build mention if valid
                elif re.match(mention_pattern, word):
                    user_did = getattr(get_user(client, word[1:]), "did", None)
                    rich_post.mention(word, user_did) if user_did else rich_post.text(word)
                # add regular text
                else:
                    rich_post.text(word)
    return rich_post, link_embed


#====================BLUESKY: SEND POST====================#
def send_post(content, **kwargs):
    access_token = kwargs.get("access_token")
    account_id = kwargs.get("account_id")
    bluesky = kwargs.get("bluesky")
    params = kwargs.get("params", {})
    post_id = kwargs.get("post_id")
    receiver = kwargs.get("receiver")
    # visibility = kwargs.get("visibility")

    # set up bluesky
    if not (bluesky or (bluesky := instantiate(access_token, account_id))):
        log_message = message("LOG_EVENT", event="Bluesky has failed to be instantiated")
        logger.warning(log_message)
        return

    if receiver:
        content = "@%s %s" % (receiver.strip(), content)
        # if not visibility:
        #     visibility = "direct"

    # make post rich
    content, link_embed = build_rich_post(bluesky, content, embed_only=True)

    # include link embed object if applicable
    params.update(embed=link_embed) if link_embed else None

    # send bluesky post
    # NOTE: post update not currently supported on bluesky - alternative implementation would be to quote instead
    if post_id:
        quote_embed = atproto_models.app.bsky.embed.record.Main(
            record=atproto_models.ComAtprotoRepoStrongRef.Main(
                uri=post_id.split(",")[0],
                cid=post_id.split(",")[1]
            )
        )
        params.update(embed=quote_embed) if not link_embed else params.update(embed=atproto_models.AppBskyEmbedRecordWithMedia.Main(record=quote_embed, media=link_embed))
    post = bluesky.send_post(text=content, **params)

    # return post id
    return "%s,%s" % (getattr(post, "uri"), getattr(post, "cid"))


#====================BLUESKY: CHECK HEALTH====================#
def check_health(**kwargs):
    account_objects = kwargs.get("account_objects", get_active_accounts(host="bluesky"))
    # visibility = "private"

    if not account_objects:
        log_message = message("LOG_EVENT", event="No active account objects were found")
        logger.info(log_message)
        return

    for account in account_objects:
        access_token = getattr(account, "access_token")
        api_base_url = getattr(account, "api_base_url")
        api_domain = get_domain(api_base_url)
        uid = getattr(account, "uid")
        # format a unique account id
        account_id = "%s.%s" % (uid, api_domain) if api_domain and uid else None
        content = message("BLUESKY_TEST", id=account_id)
        try:
            # send test post
            send_post(
                content,
                access_token=access_token,
                account_id=account_id,
                # visibility=visibility
            )
        except Exception as e:
            verbose_error = 'Test post to "%s" has failed to be sent' % account_id
            log_error = message("LOG_EXCEPT", exception=e, verbose=verbose_error, object=content)
            logger.error(log_error)
        else:
            log_message = message("LOG_EVENT", event='Test post to "%s" has been sent' % account_id)
            logger.info(log_message)


#====================BLUESKY: UPDATE ACCOUNT====================#
def update_account(**kwargs):
    access_token = kwargs.get("access_token")
    account_id = kwargs.get("account_id")
    bluesky = kwargs.get("bluesky")

    # set up bluesky
    if not (bluesky or (bluesky := instantiate(access_token, account_id))):
        log_message = message("LOG_EVENT", event="Bluesky has failed to be instantiated")
        logger.warning(log_message)
        return

    # get current profile
    current_profile_record = bluesky.app.bsky.actor.profile.get(bluesky.me.did, "self")
    current_profile = getattr(current_profile_record, "value", None)

    # NOTE: this feature is experimental - build fields into description
    description = kwargs.get("description", getattr(current_profile, "description", None))
    if fields := kwargs.get("fields"):
        if description:
            description += "\n\n"
        else:
            description = ""
        for field in fields:
            description += "%s: %s\n" % (field[0], field[1])
        description = description.rstrip("\n")

    params = dict(
        avatar=kwargs.get("avatar", getattr(current_profile, "avatar", None)), # not officially supported
        banner=kwargs.get("banner", getattr(current_profile, "banner", None)), # not officially supported
        created_at=kwargs.get("created_at", getattr(current_profile, "created_at", None)), # not officially supported
        description=description,
        display_name=kwargs.get("display_name", getattr(current_profile, "display_name", None)),
        joined_via_starter_pack=kwargs.get("joined_via_starter_pack", getattr(current_profile, "joined_via_starter_pack", None)), # not officially supported
        labels=kwargs.get("labels", getattr(current_profile, "labels", None)), # not officially supported
        pinned_post=kwargs.get("pinned_post", getattr(current_profile, "pinned_post", None)), # not officially supported
    )

    # update bluesky account
    account = bluesky.com.atproto.repo.put_record(
        atproto_models.ComAtprotoRepoPutRecord.Data(
            collection=atproto_models.ids.AppBskyActorProfile,
            repo=bluesky.me.did,
            rkey="self",
            swap_record=getattr(current_profile_record, "cid", None),
            record=atproto_models.AppBskyActorProfile.Record(**params),
        )
    )
    if account:
        account_id = bluesky.me.handle
        log_message = message("LOG_EVENT", event='Bluesky account "%s" has been updated' % account_id)
        logger.info(log_message)
    return account


#====================BLUESKY: GET USER====================#
def get_user(client, handle):
    user = None
    try:
        user = client.get_profile(handle)
    except Exception as e:
        verbose_error = 'Failed to get user "%s" profile' % handle
        log_error = message("LOG_EXCEPT", exception=e, verbose=verbose_error, object=handle)
        logger.error(log_error)
    return user
