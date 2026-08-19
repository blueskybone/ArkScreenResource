## 更新资源脚本

```bash
# 预览 PRTS 中新增的模组与职业分支图标
python3 resource_tools/update_resources.py

# 下载缺失图片
python3 resource_tools/update_resources.py --write
```

两个资源也可以单独更新：

```bash
python3 resource_tools/update_equip.py
python3 resource_tools/update_subprofession.py
```

- `skill/` 当前不参与自动更新。