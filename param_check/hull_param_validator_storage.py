"""
船体参数校验与存储模块 - 简洁版
"""

from typing import Dict, List, Tuple, Optional

class HullBasicParams:
    def __init__(self):
        self.Lpp = 0.0  # 垂线间长
        self.B = 0.0    # 船宽
        self.D = 0.0    # 型深
        self.T = 0.0    # 吃水
        self.Delta = 0.0  # 排水量

class HullParamValidator:
    @staticmethod
    def validate(params: HullBasicParams) -> Tuple[bool, List[str]]:
        errors = []
        
        # 基础校验
        if params.Lpp <= 0: errors.append("垂线间长必须大于0")
        if params.B <= 0: errors.append("船宽必须大于0") 
        if params.D <= 0: errors.append("型深必须大于0")
        if params.T <= 0: errors.append("吃水必须大于0")
        if params.Delta <= 0: errors.append("排水量必须大于0")
        
        # 规则校验
        if params.Lpp <= params.B: errors.append("船长必须大于船宽")
        if params.T >= params.D: errors.append("吃水必须小于型深")
        
        return len(errors) == 0, errors

class HullParamManager:
    def __init__(self):
        self._params = None
        self._is_valid = False
    
    def store_params(self, params_dict: Dict) -> Tuple[bool, List[str]]:
        # 创建参数对象
        params = HullBasicParams()
        for key, value in params_dict.items():
            if hasattr(params, key):
                setattr(params, key, float(value))
        
        # 验证参数
        is_valid, errors = HullParamValidator.validate(params)
        
        if is_valid:
            self._params = params
            self._is_valid = True
        
        return is_valid, errors
    
    def get_params(self):
        return self._params if self._is_valid else None

def test_module():
    print("船体参数校验测试")
    print("=" * 40)
    
    manager = HullParamManager()
    
    # 测试1: 有效参数
    print("\n1. 有效参数测试:")
    params1 = {'Lpp': 100, 'B': 20, 'D': 18, 'T': 8, 'Delta': 5000}
    valid, errors = manager.store_params(params1)
    print(f"参数: {params1}")
    print(f"结果: {'通过' if valid else '失败'}")
    if errors:
        for err in errors: print(f"  - {err}")
    
    # 测试2: 无效参数
    print("\n2. 无效参数测试:")
    params2 = {'Lpp': 50, 'B': 60, 'D': 8, 'T': 10, 'Delta': -100}
    valid, errors = manager.store_params(params2)
    print(f"参数: {params2}")
    print(f"结果: {'通过' if valid else '失败'}")
    if errors:
        for err in errors: print(f"  - {err}")
    
    # 测试3: 边界情况
    print("\n3. 边界情况测试:")
    params3 = {'Lpp': 100, 'B': 100, 'D': 10, 'T': 10, 'Delta': 0}
    valid, errors = manager.store_params(params3)
    print(f"参数: {params3}")
    print(f"结果: {'通过' if valid else '失败'}")
    if errors:
        for err in errors: print(f"  - {err}")
    
    # 最终状态
    print("\n最终状态:")
    stored = manager.get_params()
    if stored:
        print("有存储的有效参数")
    else:
        print("无有效参数")

if __name__ == "__main__":
    test_module()