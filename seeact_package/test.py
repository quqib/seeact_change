# -*- coding: utf-8 -*-
import time
from .BaseElement import BaseElement


class SelectElement(BaseElement):
    """下拉控件元素类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_element_type(self):
        """识别下拉框所属的 UI 框架类型"""
        class_names = self._ele.attr("class") or ""
        ele_type = ""

        if "el-input" in class_names or "el-select" in class_names:
            ele_type = "elementui"
        elif "ant-select" in class_names:
            ele_type = "antdesign"
        elif "form-select" in class_names:
            ele_type = "bootstrap"
        elif "ui-selectmenu" in class_names:
            ele_type = "jqueryui"
        elif "layui-" in class_names:
            ele_type = "layui"
        elif not class_names and "next-select" in self._ele.parent().attr("class"):
            ele_type = "fusion"

        return ele_type

    def _crawl_value(self, result):
        """将列表格式化为字符串（用于返回值）"""
        return ", ".join(result)

    def get_value(self):
        """获取当前选中值"""
        tag_name = self._ele.tag

        # 原生 select 或 option 元素
        if tag_name in ("select", "option"):
            ele = self._ele
            if tag_name == "option":
                ele = ele.parent("tag=select")
            select_options = ele.select.selected_options
            result = []
            for op in select_options:
                text = op.text or ""
                if text and text not in result:
                    result.append(text)
            return ", ".join(result)

        ele_type = self.get_element_type()
        if ele_type == "elementui":
            return self.get_element_ui_value()
        elif ele_type == "antdesign":
            return self.get_ant_value()
        elif ele_type == "jqueryui":
            return self.get_jquery_value()
        elif ele_type == "layui":
            return self.get_layui_value()
        elif ele_type == "fusion":
            return self.get_fusion_value()
        return ""

    def get_layui_value(self):
        """获取 layui 下拉框的值"""
        form_select = self._ele.parent("@class:layui-form-select")
        result = []
        selected = form_select.eles("@class:layui-this", timeout=2)
        for sel in selected:
            text = sel.text or ""
            if text and text not in result:
                result.append(text)
        return self._crawl_value(result)

    def get_jquery_value(self):
        """获取 jQuery UI 下拉框的值"""
        class_names = self._ele.attr("class") or ""
        ele = self._ele
        if "ui-selectmenu-button" not in class_names:
            ele = ele.parent("@class:ui-selectmenu-button")
        selects = ele.eles("@class:ui-selectmenu-text")
        result = []
        for sel in selects:
            text = sel.text or ""
            if text and text not in result:
                result.append(text)
        return self._crawl_value(result)

    def get_ant_value(self):
        """获取 Ant Design 下拉框的值"""
        select_ele = self._ele.parent("@class:ant-select-selector")
        selects = select_ele.eles("@class:ant-select-selection-item", timeout=1)
        result = []
        for sel in selects:
            text = sel.text or ""
            if text and text not in result:
                result.append(text)
        return self._crawl_value(result)

    def get_element_ui_value(self):
        """获取 Element UI 下拉框的值"""
        el_select = self._ele.parent("@class:el-select")
        class_name = el_select.attr("class")
        if "el-select_tags" in class_name:
            el_select = el_select.parent(1)
        tags = el_select.eles("@class:el-select_tags-text", timeout=1)
        result = []
        if tags:
            for tag in tags:
                result.append(tag.text)
        else:
            input_ele = el_select.eles("tag=input")
            if input_ele:
                result.append(input_ele[0].value)
        return self._crawl_value(result)

    def get_fusion_value(self):
        """获取 Fusion 下拉框的值"""
        class_names = self._ele.attr("class") or ""
        class_names_list = class_names.split()
        ele = self._ele
        idx = 0
        while "next-select" not in class_names_list:
            idx += 1
            ele = ele.parent()
            class_names = ele.attr("class") or ""
            class_names_list = class_names.split()
            if idx > 10:
                return ""

        result = []
        ele.scroll_to_see()
        # 复选框
        checkboxes = ele.eles("@class=next-tag-body", timeout=1)
        if checkboxes:
            for checkbox in checkboxes:
                result.append(checkbox.text)
        else:
            # 单选框
            try:
                em = ele.ele("tag=em", timeout=0.1)
                result.append(em.text)
            except Exception:
                pass
        return self._crawl_value(result)

    def set_value(self, value):
        """设置下拉框的值（支持多选，值用逗号分隔）"""
        ele_type = self.get_element_type()
        value = value or ""
        values = str(value).split(",")

        tag_name = self._ele.tag
        # 原生 select 或 option 元素
        if tag_name in ("select", "option"):
            ele = self._ele
            if tag_name == "option":
                ele = ele.parent("tag=select")
            options = ele.select.options
            selected_options = []
            for option in options:
                if option.text in values:
                    selected_options.append(option)
            ele.select_by_option(selected_options)
        elif ele_type == "elementui":
            self.set_element_value(values)
        elif ele_type == "antdesign":
            self.set_antdesign_value(values)
        elif ele_type == "jqueryui":
            self.set_query_value(values)
        elif ele_type == "layui":
            self.set_layui_value(values)
        elif ele_type == "fusion":
            self.set_fusion_value(values)

    def click_ele(self):
        """点击当前元素（辅助方法）"""
        self._ele.click()

    def set_element_value(self, values):
        """设置 Element UI 下拉框的值"""
        self.click_ele()
        selects = self._page.eles("tag=div@class:el-popper", timeout=2)
        selects_result = [e for e in selects if e.states.has_rect]
        if len(selects_result) == 1:
            select = selects_result[0]
            for v in values:
                option = select.ele(f"text={v}")
                option.scroll_to_see()
                option.click()
                time.sleep(1)
            if select.states.has_rect:
                self._ele.click()
        else:
            raise ValueError("未找到选择框")

    def set_antdesign_value(self, values):
        """设置 Ant Design 下拉框的值"""
        self.click_ele()
        selects = self._page.eles("tag=div@class:ant-select-dropdown", timeout=2)
        selects_result = [e for e in selects if e.states.has_rect]
        if len(selects_result) == 1:
            select = selects_result[0]
            for v in values:
                option = select.ele(f"text={v}")
                option.click()
                time.sleep(1)
            if select.states.has_rect:
                self.click_ele()
        else:
            raise ValueError("未找到选择框")

    def set_layui_value(self, values):
        """设置 layui 下拉框的值"""
        select_ele = self._ele.parent("@class:layui-form-select")
        self.click_ele()
        options_ele = select_ele.ele("tag=dl@class:layui-anim", timeout=2)
        for v in values:
            options = options_ele.eles(f"text={v}")
            for option in options:
                text = option.text or ""
                text = text.strip().replace("\t", "")
                if text == v:
                    option.scroll_to_see()
                    option.click()
                    time.sleep(0.5)
        if options_ele.states.has_rect:
            self.click_ele()

    def set_query_value(self, values):
        """设置 jQuery UI 下拉框的值"""
        self.click_ele()
        select_ele = self._page.ele("@class:ui-selectmenu-menu@class:ui-selectmenu-open")
        for v in values:
            eles = select_ele.eles(f"text:{v}")
            for ele in eles:
                text = ele.text.strip().replace("\t", "").replace("\n", "")
                if text == v:
                    ele.scroll_to_see()
                    ele.click()
                    time.sleep(1)
        if select_ele.states.has_rect:
            self._ele.click()

    def set_fusion_value(self, values):
        """设置 Fusion 下拉框的值"""
        self.click_ele()
        selects = self._page.eles("@tag=div@class:next-overlay-inner", timeout=2)
        selects_result = [e for e in selects if e.states.has_rect]
        if len(selects_result) == 1:
            select = selects_result[0]
            for v in values:
                option = select.ele(f"text={v}")
                option.click()
                time.sleep(1)
            if select.states.has_rect:
                self.click_ele()
        else:
            raise ValueError("未找到选择框")





exit()
# import litellm
# litellm.set_verbose = True
#
# response = litellm.completion(
#     model="ByteDance-Seed/Seed-OSS-36B-Instruct",  # 确认模型名称正确
#     messages=[{"role": "user", "content": "Hello"}],
#     custom_llm_provider="openai",
#     api_base="https://api.siliconflow.cn/v1",
#     api_key="sk-djopgpiaqvbtecyekaqftozuxkkpartbhjygxbfdjuazwpkz",   # 直接填入密钥，避免环境变量问题
#     max_tokens=100
# )
# print(response)

import litellm

litellm.set_verbose = True


# 模拟你的原有类
class TestLLMClass:
    def __init__(self, model, api_key, api_base, custom_llm_provider, temperature=0.1):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.custom_llm_provider = custom_llm_provider
        self.temperature = temperature

    def test_completion(self, model=None, max_new_tokens=None, temperature=None):
        # 构造测试prompt
        prompt1_input = [{"role": "user", "content": "测试调用是否成功"}]

        # 你的原代码逻辑（仅修改了kwargs为空，避免干扰）
        response1 = litellm.completion(
            model=model if model else self.model,
            messages=prompt1_input,
            max_tokens=max_new_tokens if max_new_tokens else 4096,
            temperature=temperature if temperature else self.temperature,
            api_base=self.api_base,
            api_key=self.api_key,
            custom_llm_provider=self.custom_llm_provider,
            **{}  # 清空kwargs，避免未知参数干扰
        )
        return response1

api_key="sk-djopgpiaqvbtecyekaqftozuxkkpartbhjygxbfdjuazwpkz",
# 测试调用
if __name__ == "__main__":
    # 初始化测试类（替换为你的真实配置）
    llm = TestLLMClass(
        model="ByteDance-Seed/Seed-OSS-36B-Instruct",
        api_key="sk-xxxxxxx.....",
        api_base="https://api.siliconflow.cn/v1",
        custom_llm_provider="openai"
    )

    # 执行测试
    try:
        res = llm.test_completion()
        print("测试成功，返回：", res.choices[0].message.content)
    except Exception as e:
        print("测试失败：", e)




