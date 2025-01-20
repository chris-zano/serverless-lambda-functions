const base64UrlDecode = (base64Url) => {

    let base64 = base64Url
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    while (base64.length % 4) {
        base64 += '=';
    }

    return decodeURIComponent(
        atob(base64)
            .split('')
            .map((char) => `%${`00${char.charCodeAt(0).toString(16)}`.slice(-2)}`)
            .join('')
    );
};

/**
 * Decodes a JSON Web Token (JWT) and returns its header and payload.
 *
 * @param {string} token - The JWT string to decode.
 * @returns {Object|null} An object containing the decoded header and payload as JSON objects, or null if the decoding fails.
 *
 * @throws {Error} Throws an error if the token structure is invalid.
 *
 * Example:
 * const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";
 * const decoded = decodeJWT(token);
 * console.log(decoded.header); // { alg: "HS256", typ: "JWT" }
 * console.log(decoded.payload); // { userId: "1234567890", name: "John Doe", iat: 1516239022 }
 */
const decodeJWT = (token) => {
    try {
        // Split the JWT token into its parts: header, payload, and signature
        const [header, payload, signature] = token.split('.');

        // Validate the token structure
        if (!header || !payload || !signature) {
            throw new Error('Invalid JWT token structure');
        }

        // Decode the Base64Url-encoded header and payload
        const decodedHeader = base64UrlDecode(header);
        const decodedPayload = base64UrlDecode(payload);

        // Parse the decoded header and payload into JSON objects
        const parsedHeader = JSON.parse(decodedHeader);
        const parsedPayload = JSON.parse(decodedPayload);

        console.log({ parsedHeader, parsedPayload });

        return {
            header: parsedHeader,
            payload: parsedPayload,
        };
    } catch (error) {
        console.error('Error decoding JWT:', error.message);
        return null;
    }
};
