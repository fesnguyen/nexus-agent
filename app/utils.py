import json

def extract_user_message(user_msg: list[dict[str, any]] | str):
    """
    Extract text and image list from user content
    """

    # Suppose user_msg is a list
    content_list: list[str] | str = user_msg
    if isinstance(user_msg, str):
        if user_msg.startswith("{") and user_msg.endswith("}"):
            # Content is str of list, return the wrapper str
            content_list = json.loads(user_msg)
        else:
            # Content is a pure str, return
            return user_msg, []
    elif len(content_list) == 0 \
        or not isinstance(content_list[0], dict):
        # user_msg is empty or not a dict, return empty
        return "", []

    text = ""
    image_urls = []
    # content_list is now ensured a list of dict
    for content in content_list:
        content_type = content.get("type", "")
        
        if content_type == "text":
            text += content.get("text", "")
            
        elif content_type == "image_url":
            image_data = content.get("image_url")
            if image_data and "url" in image_data:
                image_urls.append(image_data.get("url"))

    return text, image_urls