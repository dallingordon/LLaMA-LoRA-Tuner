from typing import Any, Optional, Union, Dict

import os
import json
import hashlib
from transformers import PreTrainedTokenizerBase, PreTrainedModel, AutoModelForCausalLM
from transformers.utils import cached_file

from ..config import Config
from ..models import get_tokenizer, get_model
from ..utils.download_model import download_model
# from ..lazy_import import get_torch
# from ..utils.data_processing import deep_sort_dict


class ModelPreset:
    def __init__(self, data):
        self.data = data

    @property
    def uid(self) -> str:
        return self.data['_uid']

    @property
    def name(self) -> str:
        return self.data['name']

    @property
    def model_name_or_path(self) -> str:
        return self.data['model']['name_or_path']

    @property
    def load_model_from(self) -> str:
        return self.data['model'].get('load_from') or 'default'

    @property
    def is_using_custom_tokenizer(self) -> bool:
        use_custom_tokenizer = self.data.get('use_custom_tokenizer')
        if use_custom_tokenizer is False:
            return False

        custom_tokenizer = self.data.get('custom_tokenizer')
        if not custom_tokenizer:
            return False

        if custom_tokenizer.get('name_or_path'):
            return True
        return False

    @property
    def tokenizer_name_or_path(self) -> str:
        if not self.is_using_custom_tokenizer:
            return self.data['model']['name_or_path']
        else:
            return self.data['custom_tokenizer']['name_or_path']

    @property
    def load_tokenizer_from(self) -> str:
        if not self.is_using_custom_tokenizer:
            return self.data['model'].get('load_from') or 'default'
        else:
            return self.data['custom_tokenizer'].get('load_from') or 'default'

    @property
    def tokenizer(self) -> PreTrainedTokenizerBase:
        tokenizer_name_or_path = self.tokenizer_name_or_path
        load_tokenizer_from = self.load_tokenizer_from

        if load_tokenizer_from == 'data_dir':
            tokenizer_name_or_path = os.path.join(
                Config.models_path, tokenizer_name_or_path
            )

        return get_tokenizer(tokenizer_name_or_path, self.tokenizer_args)

    @property
    def tokenizer_args(self):
        if self.is_using_custom_tokenizer:
            custom_tokenizer_args = self.data['custom_tokenizer'].get('args')
            if custom_tokenizer_args:
                return custom_tokenizer_args

        tokenizer_data = self.data.get('tokenizer', {})
        return tokenizer_data.get('args', {})

    @property
    def tokenizer_skip_special_tokens(self):
        skip_special_tokens = True
        if self.is_using_custom_tokenizer:
            if self.data['custom_tokenizer'].get('skip_special_tokens') is False:
                skip_special_tokens = False

        if skip_special_tokens:
            tokenizer_data = self.data.get('tokenizer', {})
            if tokenizer_data.get('skip_special_tokens') is False:
                skip_special_tokens = False

        return skip_special_tokens

    @property
    def model_class(self):
        return self.data['model'].get('class')

    @property
    def model(self) -> PreTrainedModel:
        if Config.ui_dev_mode:
            return None  # type: ignore

        model_name_or_path = self.model_name_or_path
        load_model_from = self.load_model_from

        if load_model_from == 'data_dir':
            model_name_or_path = os.path.join(
                Config.models_path, model_name_or_path
            )

        adapter_model_name_or_path = self.adapter_model_name_or_path
        load_adapter_model_from = self.load_adapter_model_from

        if (
            adapter_model_name_or_path
            and load_adapter_model_from == 'data_dir'
        ):
            adapter_model_name_or_path = os.path.join(
                Config.adapter_models_path, adapter_model_name_or_path
            )

        return get_model(
            model_name_or_path,
            self.model_args,
            cls=self.model_class,
            adapter_model_name_or_path=adapter_model_name_or_path,
        )

    @property
    def adapter_model_name_or_path(self) -> Union[str, None]:
        use_adapter_model = self.data.get('use_adapter_model')
        if use_adapter_model is False:
            return None

        adapter_model = self.data.get('adapter_model')
        if not adapter_model:
            return None

        return self.data['adapter_model'].get('name_or_path')

    @property
    def load_adapter_model_from(self) -> str:
        return self.data['model'].get('load_from') or 'default'

    @property
    def model_args(self) -> Dict[str, Any]:
        args = self.data['model'].get('args')
        if not args:
            args = {}

        if args.get('load_in_8bit') is None:
            args['load_in_8bit'] = Config.default_load_in_8bit

        if args.get('torch_dtype') is None:
            args['torch_dtype'] = Config.default_torch_dtype

        if args.get('device_map') is None:
            args['device_map'] = Config.default_device_map

        return args

    @property
    def default_prompt_template(self):
        defaults = self.data.get('defaults')
        if not defaults:
            return 'None'
        return defaults.get('prompt_template', 'None')

    def download_and_cache_model(self):
        if self.load_model_from == 'data_dir':
            return

        model_name = self.data['model']['name_or_path']
        args = self.data['model'].get('args', {})

        download_model(model_name, args)

    # @property
    # def model_hash(self) -> str:
    #     model_data = deep_sort_dict(self.data['model'])
    #     json_value = json.dumps(model_data, ensure_ascii=False).encode('utf-8')
    #     return hashlib.sha256(json_value).hexdigest()

    # @property
    # def adapter_model_hash(self) -> str:
    #     adapter_model = self.data.get('adapter_model')
    #     if not adapter_model:
    #         return 'None'

    #     json_value = json.dumps(
    #         adapter_model, ensure_ascii=False).encode('utf-8')
    #     return hashlib.sha256(json_value).hexdigest()
