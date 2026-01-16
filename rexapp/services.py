import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def criar_produto_stripe(produto):
    """
    Cria um produto no Stripe com preço e retorna product_id e price_id
    """
    try:
        # Cria o produto no Stripe
        stripe_product = stripe.Product.create(
            name=produto.nome,
            description=produto.especificacoes,
        )
        
        product_id = stripe_product.id
        
        # Cria o preço para o produto
        # Converte o preço para centavos (Stripe usa centavos)
        preco_em_centavos = int(produto.preco * 100)
        
        stripe_price = stripe.Price.create(
            product=product_id,
            unit_amount=preco_em_centavos,
            currency="brl",  # Ou a moeda que você usar
        )
        
        price_id = stripe_price.id
        
        # Retorna ambos os IDs
        return {
            "product_id": product_id,
            "price_id": price_id
        }
    
    except stripe.error.StripeError as e:
        print(f"Erro ao criar produto no Stripe: {str(e)}")
        return None
