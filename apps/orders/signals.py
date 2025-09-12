import africastalking
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Order

@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Send SMS to customer and email to admin when an order is created
    """
    if created:
        # Send SMS to customer
        send_sms_notification(instance)
        
        # Send email to admin
        send_email_notification(instance)

def send_sms_notification(order):
    """
    Send SMS notification to customer using Africa's Talking
    """
    try:
        # Initialize Africa's Talking
        username = settings.AFRICASTALKING_USERNAME
        api_key = settings.AFRICASTALKING_API_KEY
        
        if not username or not api_key:
            print("Africa's Talking credentials not configured")
            return
        
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        
        # Prepare message
        message = f"Thank you for your order #{order.id}. Your order has been received and is being processed."
        recipient = order.customer.phone_number
        
        # Send SMS
        response = sms.send(message, [recipient], settings.AFRICASTALKING_SENDER)
        print(f"SMS sent to {recipient}: {response}")
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")

def send_email_notification(order):
    """
    Send email notification to admin
    """
    try:
        # Prepare email content
        subject = f"New Order #{order.id} Received"
        
        # Get order items
        items = []
        for item in order.items.all():
            items.append({
                'product': item.product.name,
                'quantity': item.quantity,
                'price': item.price,
                'subtotal': item.subtotal
            })
        
        # Prepare context for email template
        context = {
            'order_id': order.id,
            'customer_name': f"{order.customer.user.first_name} {order.customer.user.last_name}",
            'customer_email': order.customer.user.email,
            'customer_phone': order.customer.phone_number,
            'shipping_address': order.shipping_address,
            'total_amount': order.total_amount,
            'items': items,
            'created_at': order.created_at,
        }
        
        # Render email content
        message = f"""
        Order Details:
        Order ID: {order.id}
        Customer: {context['customer_name']}
        Email: {context['customer_email']}
        Phone: {context['customer_phone']}
        Shipping Address: {context['shipping_address']}
        Total Amount: ${context['total_amount']}
        
        Order Items:
        """
        
        for item in items:
            message += f"\n- {item['quantity']} x {item['product']} (${item['price']} each) = ${item['subtotal']}"
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        print(f"Email notification sent to admin for Order #{order.id}")
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
