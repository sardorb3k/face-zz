"""
Face recognition using InsightFace/ArcFace
"""
import cv2
import numpy as np
import onnxruntime as ort
from typing import Optional, List, Tuple
import os
from pathlib import Path


class FaceRecognitionService:
    """InsightFace/ArcFace yordamida yuz tanib olish"""
    
    def __init__(self, model_name: str = "buffalo_l"):
        """
        Face recognition service ni ishga tushirish
        
        Args:
            model_name: Model nomi (buffalo_l - best accuracy, buffalo_s - faster, arcface_r100_v1 - legacy)
        """
        # Default to buffalo_l for best accuracy
        if model_name == "arcface_r100_v1":
            model_name = "buffalo_l"
        
        self.model_name = model_name
        self.model = None
        self.input_size = (112, 112)  # ArcFace uchun standart o'lcham
        self.use_insightface_package = False
        self.insightface_app = None
        
        # Model yo'lini aniqlash
        model_dir = Path(os.getenv("MODEL_DIR", "./models"))
        model_dir.mkdir(exist_ok=True, parents=True)
        
        # Model yuklash (agar mavjud bo'lsa)
        self._load_model(model_dir)
    
    def _load_model(self, model_dir: Path):
        """Model yuklash - bir nechta usulni qo'llab-quvvatlaydi"""
        # InsightFace models papkasini yaratish (agar yo'q bo'lsa)
        insightface_dir = model_dir / "insightface_models"
        insightface_dir.mkdir(exist_ok=True, parents=True)
        
        # Model qidirish tartibi:
        # 1. InsightFace models papkasida (buffalo_l.onnx, w600k_r50.onnx, yoki buffalo_l/ papkasi)
        # 2. Models papkasida to'g'ridan-to'g'ri
        # 3. Environment variable orqali
        # 4. InsightFace package orqali (fallback)
        
        model_path = None
        
        # 1. InsightFace models papkasida qidirish
        possible_names = [
            f"{self.model_name}.onnx",  # buffalo_l.onnx
            "w600k_r50.onnx",  # Buffalo_l recognition model nomi
            "glintr100.onnx",  # Alternative recognition model
        ]
        
        # 1a. InsightFace models papkasida to'g'ridan-to'g'ri
        for name in possible_names:
            test_path = insightface_dir / name
            if test_path.exists():
                model_path = test_path
                print(f"🔍 Model topildi: {test_path}")
                break
        
        # 1b. Buffalo_l papkasi ichida (to'liq model strukturasida)
        if model_path is None:
            buffalo_dir = insightface_dir / "buffalo_l"
            if buffalo_dir.exists():
                # Recognition model qidirish
                rec_models = ["w600k_r50.onnx", "glintr100.onnx", f"{self.model_name}.onnx"]
                for rec_name in rec_models:
                    rec_path = buffalo_dir / rec_name
                    if rec_path.exists():
                        model_path = rec_path
                        print(f"🔍 Model topildi (buffalo_l papkasida): {rec_path}")
                        break
        
        # 2. Models papkasida to'g'ridan-to'g'ri qidirish
        if model_path is None:
            for name in possible_names:
                test_path = model_dir / name
                if test_path.exists():
                    model_path = test_path
                    print(f"🔍 Model topildi: {test_path}")
                    break
        
        # 3. Environment variable orqali
        if model_path is None:
            env_model_path = os.getenv("FACE_RECOGNITION_MODEL_PATH")
            if env_model_path and Path(env_model_path).exists():
                model_path = Path(env_model_path)
        
        # Model yuklash
        if model_path and model_path.exists():
            try:
                providers = ['CPUExecutionProvider']
                if os.getenv("USE_GPU", "false").lower() == "true":
                    try:
                        if 'CUDAExecutionProvider' in ort.get_available_providers():
                            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                            print("   GPU ishlatilmoqda...")
                    except:
                        pass
                
                self.model = ort.InferenceSession(str(model_path), providers=providers)
                print(f"✅ ONNX Model yuklandi: {model_path}")
                return  # ONNX model yuklandi, InsightFace package kerak emas
            except Exception as e:
                print(f"⚠️  ONNX Model yuklashda xatolik: {e}")
                # InsightFace package orqali yuklashga urinish
                self._try_insightface_package()
        else:
            # Model topilmadi, InsightFace package orqali yuklash
            print(f"ℹ️  ONNX model topilmadi, InsightFace package orqali yuklanmoqda...")
            self._try_insightface_package()
    
    def _try_insightface_package(self):
        """InsightFace Python package orqali model yuklash"""
        try:
            import insightface
            print("📦 InsightFace package orqali model yuklanmoqda...")
            
            # Model nomini tekshirish - InsightFace 0.7+ da 'buffalo_l' yoki 'buffalo_s' ishlatiladi
            model_name = self.model_name
            if model_name not in ["buffalo_l", "buffalo_s", "buffalo_m", "buffalo_x"]:
                # Eski yoki noto'g'ri model nomi, default model ishlatish (buffalo_l - best accuracy)
                model_name = "buffalo_l"
                print(f"   Model nomi '{self.model_name}' noto'g'ri, eng yaxshi model ishlatilmoqda (buffalo_l)...")
            
            # GPU yoki CPU ishlatish
            providers = ['CPUExecutionProvider']
            if os.getenv("USE_GPU", "false").lower() == "true":
                try:
                    import onnxruntime
                    if 'CUDAExecutionProvider' in onnxruntime.get_available_providers():
                        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                        print("   GPU ishlatilmoqda...")
                except:
                    pass
            
            # InsightFace app yaratish (avtomatik model yuklaydi)
            self.insightface_app = insightface.app.FaceAnalysis(
                name=model_name,  # buffalo_l - best accuracy, buffalo_s - faster
                providers=providers
            )
            self.insightface_app.prepare(ctx_id=0, det_size=(640, 640))
            
            # InsightFace API ishlatish
            self.use_insightface_package = True
            print(f"✅ InsightFace package orqali model yuklandi! (Model: {model_name})")
        except ImportError:
            print("⚠️  InsightFace package o'rnatilmagan")
            print("💡 O'rnatish: pip install insightface")
        except Exception as e:
            print(f"⚠️  InsightFace package orqali yuklashda xatolik: {e}")
            self.use_insightface_package = False
    
    def create_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """
        Rasmdan embedding yaratish (ALIGNMENT bilan - to'g'ri usul)
        
        Args:
            image_path: Rasm fayl yo'li
            
        Returns:
            Face embedding (512-dimensional vector, L2 normalized) yoki None
        """
        # Rasmni yuklash
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # InsightFace package ishlatilsa - get() metodi alignment qiladi
        if self.use_insightface_package and self.insightface_app:
            try:
                # InsightFace get() metodi:
                # 1. Face detection (SCRFD)
                # 2. Landmark detection (5 yoki 106 nuqta)
                # 3. Alignment (affine transformation)
                # 4. Resize 112x112
                # 5. Normalize
                # 6. Embedding yaratish
                faces = self.insightface_app.get(image)
                
                if not faces or len(faces) == 0:
                    print("⚠️  Rasmda yuz topilmadi")
                    return None
                
                # Eng katta yuzni olish (agar bir nechta bo'lsa)
                face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
                
                # norm_embedding allaqachon normalizatsiya qilingan va aligned
                if face.norm_embedding is None:
                    # Try to get embedding manually if norm_embedding is None
                    print("⚠️  norm_embedding None, embedding dan yaratilmoqda...")
                    # Sometimes norm_embedding might be None, try to compute it from embedding
                    if hasattr(face, 'embedding') and face.embedding is not None:
                        embedding = face.embedding.astype(np.float32)
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            embedding = embedding / norm
                            return embedding
                    # If embedding also None, try to get it from recognition model directly
                    if hasattr(self.insightface_app, 'models') and self.insightface_app.models and 'recognition' in self.insightface_app.models:
                        try:
                            # Extract face region and create embedding manually
                            bbox = face.bbox.astype(int)
                            x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                            face_crop = image[y1:y2, x1:x2]
                            if face_crop.size > 0:
                                embedding = self.create_embedding_from_array(face_crop)
                                if embedding is not None:
                                    return embedding
                        except Exception as e:
                            print(f"⚠️  Manual embedding yaratishda xatolik: {e}")
                    return None
                
                embedding = face.norm_embedding.astype(np.float32)
                
                # Normalizatsiyani tekshirish (1.0 ga yaqin bo'lishi kerak)
                norm = np.linalg.norm(embedding)
                if abs(norm - 1.0) > 0.01:
                    # Qayta normalizatsiya qilish
                    embedding = embedding / norm
                
                return embedding
            except Exception as e:
                print(f"⚠️  InsightFace embedding yaratishda xatolik: {e}")
                return None
        
        # Fallback: ONNX model (alignment yo'q, lekin ishlaydi)
        try:
            # Yuzni kesib olish (butun rasm yuz bo'lishi mumkin)
            face_image = image
            
            # Preprocessing (alignment yo'q)
            face_preprocessed = self.preprocess_face(face_image)
            
            if self.model is None:
                print("⚠️  Model yuklanmagan")
                return None
            
            # Inference
            input_name = self.model.get_inputs()[0].name
            output = self.model.run(None, {input_name: face_preprocessed})
            
            # Embedding olish
            embedding = output[0][0]
            
            # Normalizatsiya (L2 normalization) - MUHIM!
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            else:
                return None
            
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"Embedding yaratishda xatolik: {e}")
            return None
    
    def create_embedding_from_array(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        NumPy array dan embedding yaratish
        
        Args:
            face_image: Yuz rasmi (BGR format)
            
        Returns:
            Face embedding yoki None
        """
        # InsightFace package ishlatilsa
        if self.use_insightface_package and self.insightface_app:
            try:
                # InsightFace app'da recognition modelini olish
                if hasattr(self.insightface_app, 'models') and self.insightface_app.models and 'recognition' in self.insightface_app.models:
                    # To'g'ridan-to'g'ri recognition modelini ishlatish
                    rec_model = self.insightface_app.models['recognition']
                    
                    # Yuz rasmini preprocess qilish (112x112, RGB, normalized)
                    face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB) if len(face_image.shape) == 3 and face_image.shape[2] == 3 else face_image
                    face_resized = cv2.resize(face_rgb, (112, 112))
                    face_normalized = face_resized.astype(np.float32)
                    
                    # InsightFace'ning standart preprocessing'i
                    # Buffalo model uchun: (img - 127.5) / 128.0
                    face_normalized = (face_normalized - 127.5) / 128.0
                    face_batch = np.expand_dims(face_normalized.transpose(2, 0, 1), axis=0)
                    
                    # Inference
                    embedding = rec_model.run(None, {'data': face_batch})[0][0]
                    embedding = embedding / np.linalg.norm(embedding)
                    return embedding.astype(np.float32)
                else:
                    # Eski usul: get() metodi orqali (agar recognition model topilmasa)
                    faces = self.insightface_app.get(face_image)
                    
                    # Tekshirish: faces None yoki bo'sh bo'lishi mumkin
                    if not faces or len(faces) == 0:
                        # Yuz topilmadi, fallback ga o'tish
                        raise ValueError("InsightFace get() metodi yuz topa olmadi")
                    
                    # Eng katta yuzni olish (agar bir nechta bo'lsa)
                    # Barcha face'larda norm_embedding borligini tekshirish
                    valid_faces = [f for f in faces if hasattr(f, 'norm_embedding') and f.norm_embedding is not None]
                    
                    if not valid_faces:
                        # Hech qanday valid embedding yo'q
                        raise ValueError("Valid embedding topilmadi")
                    
                    # Eng katta yuzni topish
                    face = max(valid_faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
                    
                    # Embedding'ni tekshirish
                    if face.norm_embedding is None:
                        raise ValueError("Face norm_embedding None")
                    
                    embedding = face.norm_embedding
                    
                    # Embedding numpy array ekanligini va to'g'ri o'lchamda ekanligini tekshirish
                    if embedding is None or not isinstance(embedding, np.ndarray):
                        raise ValueError("Embedding not a valid numpy array")
                    
                    return embedding.astype(np.float32)
            except (AttributeError, ValueError, KeyError, TypeError) as e:
                # Attribute, value, key yoki type xatolik, fallback ga o'tish
                pass
            except Exception as e:
                # Boshqa xatoliklar, fallback ga o'tish
                pass
        
        # ONNX model fallback (agar InsightFace ishlamasa)
        # Yoki InsightFace package ishlatilmasa
        try:
            face_preprocessed = self.preprocess_face(face_image)
            
            if self.model is None:
                # Model yo'q, lekin InsightFace ham ishlamadi
                # Bu holatda None qaytarish yaxshiroq (dummy embedding emas)
                return None
            
            input_name = self.model.get_inputs()[0].name
            output = self.model.run(None, {input_name: face_preprocessed})
            embedding = output[0][0]
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"⚠️  ONNX model fallback ham ishlamadi: {e}")
            return None
    
    def preprocess_face(self, face_image: np.ndarray) -> np.ndarray:
        """
        Yuz rasmini model uchun tayyorlash
        
        Args:
            face_image: Yuz rasmi (BGR format)
            
        Returns:
            Preprocessed image (RGB, normalized, resized)
        """
        # BGR dan RGB ga o'tkazish
        if len(face_image.shape) == 3 and face_image.shape[2] == 3:
            face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        else:
            face_rgb = face_image
        
        # O'lchamni o'zgartirish
        face_resized = cv2.resize(face_rgb, self.input_size)
        
        # Normalizatsiya
        face_normalized = face_resized.astype(np.float32) / 255.0
        face_normalized = (face_normalized - 0.5) / 0.5  # [-1, 1] oraliq
        
        # Batch dimension qo'shish
        face_batch = np.expand_dims(face_normalized, axis=0)
        
        # Transpose (NCHW format)
        face_batch = np.transpose(face_batch, (0, 3, 1, 2))
        
        return face_batch
    
    def compare_faces(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        threshold: float = 0.4
    ) -> Tuple[bool, float]:
        """
        Ikki embedding'ni solishtirish
        
        Args:
            embedding1: Birinchi embedding
            embedding2: Ikkinchi embedding
            threshold: O'xshashlik chegarasi (default 0.4)
            
        Returns:
            (match, similarity_score) tuple
        """
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2)
        
        # Threshold dan yuqori bo'lsa, bir xil odam
        match = similarity >= threshold
        
        return match, float(similarity)
    
    def find_matching_student(
        self,
        embedding: np.ndarray,
        students: List[Tuple[int, np.ndarray]],
        threshold: float = 0.4
    ) -> Optional[Tuple[int, float]]:
        """
        Eng o'xshash talabani topish
        
        Args:
            embedding: Qidirilayotgan embedding
            students: List of (student_id, embedding) tuples
            threshold: O'xshashlik chegarasi
            
        Returns:
            (student_id, similarity) yoki None
        """
        best_match = None
        best_similarity = threshold
        
        for student_id, student_embedding in students:
            match, similarity = self.compare_faces(embedding, student_embedding, threshold)
            
            if match and similarity > best_similarity:
                best_similarity = similarity
                best_match = (student_id, similarity)
        
        return best_match
