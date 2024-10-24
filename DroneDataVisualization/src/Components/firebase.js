import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAyCCPjo89hHdQ8-2duyeVBrVMl4CQljJo",
    authDomain: "airecondrone.firebaseapp.com",
    databaseURL: "https://airecondrone-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "airecondrone",
    storageBucket: "airecondrone.appspot.com",
    messagingSenderId: "961986898365",
    appId: "1:961986898365:web:6ed5dfb4c3b2aa4a3f0ad4",
    measurementId: "G-E14P5GN8H8"
};

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);

// Initialize Firestore
const db = getFirestore(firebaseApp);

// Initialize Storage
const storage = getStorage(firebaseApp);

// Export the instances
export { db, storage };