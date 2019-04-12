from django.db import models

# Create your models here.


from meiduo_mall.utils.models import BaseModel


class GoodsCategory(BaseModel):
    """商品类别"""
    name = models.CharField(max_length=10,verbose_name="名称")
    parent = models.ForeignKey('self',related_name='subs',null=True,
                               blank=True,on_delete=models.CASCADE,verbose_name="父类别")

    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsChannelGroup(BaseModel):
    """商品频道组"""
    # id = models.IntegerField(max_length=10, verbose_name='频道组号')
    name = models.CharField(max_length=20, verbose_name='频道组名')

    class Meta:
        db_table = 'tb_channel_group'
        verbose_name = '商品频道组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
    pass

class GoodsChannel(BaseModel):
    """商品频道"""

    group = models.ForeignKey(GoodsChannelGroup,verbose_name='频道组号')
    category = models.ForeignKey(GoodsCategory,on_delete=models.CASCADE,verbose_name='顶级商品类别')
    url = models.CharField(max_length=50,verbose_name='频道页面链接')
    sequence = models.IntegerField(verbose_name="组内序号")

    class Meta:
        db_table = 'tb_goods_channel'
        verbose_name = "商品频道"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name

class Brand(BaseModel):
    """商品品牌"""

    name = models.CharField(max_length=10,verbose_name='品牌名称')
    logo = models.ImageField(verbose_name='logo图片')
    first_letter=models.CharField(max_length=10,verbose_name='品牌首字母')

    class Meta:
        db_table = 'tb_brand'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class SPU(BaseModel):

    """商品信息"""
    name = models.CharField(max_length=50, verbose_name='名称')
    brand_id = models.ForeignKey(Brand,verbose_name='品牌id')
    category1_id = models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,related_name='cat1_spu',verbose_name='一级类别id')
    category2_id = models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,related_name='cat2_spu',verbose_name='二级类别id')
    category3_id = models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,related_name='cat3_spu',verbose_name='三级类别id')
    sales = models.IntegerField(verbose_name='销量')
    comments = models.IntegerField(default=0, verbose_name='评价数')
    desc_detail = models.TextField(default='', verbose_name='详细介绍')
    desc_pack = models.TextField(default='', verbose_name='包装信息')
    desc_service = models.TextField(default='', verbose_name='售后服务')

    class Meta:
        db_table = 'tb_spu'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class SKU(BaseModel):
    """商品库存"""
    name = models.CharField(max_length=50, verbose_name='名称')
    caption = models.CharField(max_length=100, verbose_name='副标题')
    spu_id = models.ForeignKey(SPU,related_name='skus',on_delete=models.CASCADE,verbose_name='商品id')
    category_id = models.ForeignKey(GoodsCategory,on_delete=models.PROTECT,verbose_name='三级类别id')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='进价')
    market_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='市场价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    comments = models.IntegerField(default=0, verbose_name='评价数')
    is_launched = models.BooleanField(default=True, verbose_name='是否上架销售')
    default_image = models.ImageField(max_length=200, default='', null=True, blank=True, verbose_name='默认图片')

    class Meta:
        db_table = 'tb_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name


    def __str__(self):
        return '%s:%s'%(self.id,self.name)

class SKUImage(BaseModel):
    """商品图片链接"""
    sku_id = models.ForeignKey(SKU,on_delete=models.CASCADE,verbose_name='所属sku id')
    image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'tb_sku_image'
        verbose_name = 'SKU图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.sku.name, self.id)

class SPUSpecification(BaseModel):
    """商品规格表"""
    spu_id = models.ForeignKey(SPU,on_delete=models.CASCADE,related_name='specs',verbose_name='商品id')
    name = models.CharField(max_length=20, verbose_name='规格名称')

    class Meta:
        db_table = 'tb_spu_specification'
        verbose_name = '商品SPU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.spu.name, self.name)

class SPUspecificationOption(BaseModel):
    """规格选项表"""
    spec_id = models.ForeignKey(SPUSpecification, related_name='options', on_delete=models.CASCADE,verbose_name='规格id')
    value = models.CharField(max_length=20, verbose_name='选项值')

    class Meta:
        db_table = 'tb_specification_option'
        verbose_name = '规格选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.spec_id, self.value)

class SKUSpecification(BaseModel):
    """库存商品规格信息表"""
    sku_id = models.ForeignKey(SKU,related_name='specs',on_delete=models.CASCADE,verbose_name="所属sku id")
    spec_id = models.ForeignKey(SPUSpecification,verbose_name='规格id')
    option_id = models.ForeignKey(SPUspecificationOption,verbose_name='选项规格id')

    class Meta:
        db_table = 'tb_sku_specification'
        verbose_name = 'SKU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s - %s' % (self.sku_id, self.spec_id.name, self.option_id.value)






