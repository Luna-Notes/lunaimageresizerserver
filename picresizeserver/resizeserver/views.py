import os
import numpy as np
import cv2
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rembg import remove
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ResizeImageSerializer  # Make sure you have this import
import io
import boto3
from django.conf import settings
from django.http import FileResponse


class ResizeImageView(APIView):
    def post(self, request):
        serializer = ResizeImageSerializer(data=request.data)

        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            new_width = serializer.validated_data['width']
            new_height = serializer.validated_data['height']

            try:
                # Read the image file into a numpy array
                image_bytes = np.frombuffer(image_file.read(), np.uint8)
                image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

                # Check if the image is valid
                if image is None:
                    return Response({"error": "Invalid image format."}, status=status.HTTP_400_BAD_REQUEST)

                # Resize the image using INTER_CUBIC for better quality
                resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

                # Convert the resized image back to PIL format
                pil_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))

                # Save the resized image to a BytesIO object
                image_io = io.BytesIO()
                pil_image.save(image_io, format='PNG')  # Save as PNG to maintain quality
                image_io.seek(0)  # Reset the stream to the beginning

                # Return the image in the response as a file response
                return FileResponse(image_io, content_type='image/png', as_attachment=True, filename='resized_image.png')

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ImageBackgroundRemoveView(APIView):
    def post(self, request):
        try:
            # Ensure the file is included in the request
            image_file = request.FILES.get('image')

            if not image_file:
                return Response({"error": "No image file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            # Load the image using Pillow
            image = Image.open(image_file)

            # Convert image to bytes for background removal
            image_io = io.BytesIO()
            image.save(image_io, format='PNG')
            image_data = image_io.getvalue()

            # Use rembg to remove the background
            output_image_data = remove(image_data)

            # Load the resulting image back into a Pillow Image object
            output_image = Image.open(io.BytesIO(output_image_data))

            # Save the resulting image to a BytesIO object
            output_io = io.BytesIO()
            output_image.save(output_io, format='PNG')
            output_io.seek(0)  # Reset the pointer to the start of the file

            # Return the image in the response as a FileResponse
            return FileResponse(output_io, content_type='image/png', as_attachment=True, filename='bg_removed.png')

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


